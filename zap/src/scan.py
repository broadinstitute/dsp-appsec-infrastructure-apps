#!/usr/bin/env python3
"""
Runs ZAP scan, uploads results to Code Dx and GCS, and alerts Slack.
"""

import logging
from os import getenv
from datetime import datetime
from enum import Enum
from typing import List

from codedx_api.CodeDxAPI import CodeDx
from google.cloud import storage
from slack_sdk.web import WebClient as SlackClient

from zap import ScanType, zap_compliance_scan


def upload_gcs(bucket_name: str, scan_type: ScanType, filename: str):
    """
    Upload scans to a GCS bucket and return the path to the file in Cloud Console.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    date = datetime.today().strftime("%Y%m%d")
    path = f"{scan_type}-scans/{date}/{filename}"
    blob = bucket.blob(path)
    blob.upload_from_filename(filename)
    return f"https://console.cloud.google.com/storage/browser/_details/{bucket_name}/{path}"


def codedx_upload(cdx: CodeDx, project: str, filename: str):
    """
    Create CodeDx project if needed and trigger analysis on the uploaded file.
    """
    cdx.update_projects()
    if project not in list(cdx.projects):
        cdx.create_project(project)
        cdx.update_projects()

    cdx.analyze(project, filename)


class Severity(str, Enum):
    """
    Provides possible values of finding severity in Code Dx.
    """

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


def get_codedx_alert_count_by_severity(
    cdx: CodeDx, project: str, severities: List[Severity]
) -> int:
    """
    Get finding count, given the severity levels for a Code Dx project.
    """
    filters = {
        "filter": {
            "severity": [s.value for s in severities],
        },
    }
    res = cdx.get_finding_count(project, filters)
    if "count" not in res:
        raise RuntimeError(f"Error fetching count: {res}")
    return res["count"]


def get_alerts_string(cdx: CodeDx, project: str, severities: List[Severity]):
    """
    Get the list of finding statistics to be shown in a Slack alert.
    """
    messages: List[str] = []
    emojis = {
        Severity.CRITICAL.value: ":stopsign:",
        Severity.HIGH.value: ":triangular_flag_on_post:",
        Severity.MEDIUM.value: ":radioactive_sign:",
        Severity.LOW.value: ":warning:",
        Severity.INFO.value: ":heavy_check_mark:",
    }
    for severity in severities:
        count = get_codedx_alert_count_by_severity(cdx, project, [severity])
        if count:
            messages.append(
                f"\t{ emojis[severity] } { count } { severity.value } findings\n"
            )
    return "".join(messages)


def get_codedx_report_by_alert_severity(
    cdx: CodeDx, project: str, severities: List[Severity]
):
    """
    Generate a PDF report, given the severity levels for a Code Dx project.
    """
    logging.info("Getting PDF report from Codedx project: %s", project)
    report_date = datetime.now()
    report_file = f'{project.replace("-", "_")}_report_{report_date:%Y%m%d}.pdf'
    filters = {
        "severity": [s.value for s in severities],
        "status": ["new", "unresolved", "reopened"],
    }
    cdx.get_pdf(
        project,
        summary_mode="detailed",
        details_mode="with-source",
        include_result_details=True,
        include_comments=True,
        include_request_response=False,
        file_name=report_file,
        filters=filters,
    )

    return report_file


SEVERITY_DELIM = "|"


def parse_severities(severities: str):
    """
    Parse the list of severities.
    """
    default_severities = SEVERITY_DELIM.join(
        (Severity.CRITICAL.value, Severity.HIGH.value)
    )
    severities = severities or default_severities
    return [Severity(s.capitalize()) for s in severities.split(SEVERITY_DELIM)]


def slack_alert_with_report(  # pylint: disable=too-many-arguments
    cdx: CodeDx,
    codedx_project: str,
    severities: List[Severity],
    token: str,
    channel: str,
    target_url: str,
    xml_report_url: str,
    scan_type: ScanType,
):
    """
    Alert Slack on requested findings, if any.
    """
    # continue only if Slack channel is set
    if not channel:
        logging.warning("Slack alert was not requested")
        return

    slack = SlackClient(token)

    gcs_slack_text = ""
    if xml_report_url:
        gcs_slack_text = (
            f"New vulnerability report uploaded to GCS bucket: {xml_report_url}\n"
        )

    if get_codedx_alert_count_by_severity(cdx, codedx_project, severities):
        # attach a full report, if there are findings
        report_file = get_codedx_report_by_alert_severity(
            cdx, codedx_project, severities
        )
        alerts_string = get_alerts_string(cdx, codedx_project, severities)
        report_message = (
            f"{ gcs_slack_text }"
            f"{scan_type} scan of endpoint { target_url } contains:\n"
            f"{ alerts_string }"
            f"Please see attached report for details."
        )
        slack.files_upload(
            channels=channel,
            file=report_file,
            title=report_file,
            initial_comment=report_message,
        )
    elif gcs_slack_text:
        # mention only XML report, if it was requested
        slack.chat_postMessage(channel=channel, text=gcs_slack_text)
    else:
        logging.warning("No findings for alert to Slack")
        return
    logging.info("Alert sent to Slack channel: %s", channel)


def main():
    """
    - Run ZAP scan
    - Upload results to Code Dx
    - Upload ZAP XML report to GCS, if needed
    - Send a Slack alert with Code Dx report, if needed.
    """
    # parse env variables
    zap_port = int(getenv("ZAP_PORT", ""))

    codedx_project = getenv("CODEDX_PROJECT")
    codedx_url = getenv("CODEDX_URL")
    codedx_api_key = getenv("CODEDX_API_KEY")

    target_url = getenv("URL")
    scan_type = ScanType(getenv("SCAN_TYPE"))

    bucket_name = getenv("BUCKET_NAME")

    slack_channel = getenv("SLACK_CHANNEL")
    slack_token = getenv("SLACK_TOKEN")

    severities = parse_severities(getenv("SEVERITIES"))

    # configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(levelname)-8s [{codedx_project} {scan_type}-scan] %(message)s",
    )
    logging.info("Severities: %s", ", ".join(s.value for s in severities))

    # run Zap scan
    zap_filename = zap_compliance_scan(codedx_project, zap_port, target_url, scan_type)

    # upload its results to Code Dx
    cdx = CodeDx(codedx_url, codedx_api_key)
    codedx_upload(cdx, codedx_project, zap_filename)

    # optionally, upload them to GCS
    xml_report_url = ""
    if scan_type == ScanType.UI:
        xml_report_url = upload_gcs(bucket_name, scan_type, zap_filename)

    # alert Slack, if needed
    slack_alert_with_report(
        cdx,
        codedx_project,
        severities,
        slack_token,
        slack_channel,
        target_url,
        xml_report_url,
        scan_type,
    )


if __name__ == "__main__":
    main()
