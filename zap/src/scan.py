#!/usr/bin/env python3

import logging
import os
from datetime import datetime
from enum import Enum
from typing import List

from codedx_api.CodeDxAPI import CodeDx
from google.cloud import storage
from slack_sdk.web import WebClient as SlackClient

from zap import ScanType, compliance_scan


def upload_gcp(bucket_name: str, scan_type: ScanType, filename: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    date = datetime.today().strftime("%Y%m%d")
    path = f"{scan_type}-scans/{date}/{filename}"
    blob = bucket.blob(path)
    blob.upload_from_filename(filename)
    location = f"https://console.cloud.google.com/storage/browser/_details/{bucket_name}/{path}"
    return location


def get_codedx_client():
    base_url = os.getenv("CODEDX_URL")
    codedx_api_key = os.getenv("CODEDX_API_KEY")
    return CodeDx(base_url, codedx_api_key)


def codedx_upload(cdx: CodeDx, project: str, filename: str):
    cdx.update_projects()
    if project not in list(cdx.projects):
        cdx.create_project(project)
        cdx.update_projects()

    cdx.analyze(project, filename)


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


def get_codedx_alert_count_by_severity(
    cdx: CodeDx, project: str, severities: List[Severity]
) -> int:
    filters = {
        "filter": {
            "severity": [s.value for s in severities],
        },
    }
    res = cdx.get_finding_count(project, filters)
    if "count" not in res:
        logging.info(f"Error fetching count: {res}")
    return res["count"]


def get_alerts_string(cdx: CodeDx, project: str, severities: List[Severity]):
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
    logging.info(f"Getting PDF report from Codedx project: {project}")
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


def main():
    # get scan variables
    codedx_project = os.getenv("CODEDX_PROJECT")
    target_url = os.getenv("URL")
    scan_type = ScanType(os.getenv("SCAN_TYPE"))
    bucket_name = os.getenv("BUCKET_NAME")
    slack_channel = os.getenv("SLACK_CHANNEL")

    default_severities = SEVERITY_DELIM.join(
        (Severity.CRITICAL.value, Severity.HIGH.value)
    )
    severities = os.getenv("SEVERITIES") or default_severities
    severities = [Severity(s.capitalize()) for s in severities.split(SEVERITY_DELIM)]

    # configure logging
    logging.basicConfig(
        level=logging.INFO, format=f"%(levelname)-8s [{codedx_project}] %(message)s"
    )
    logging.info("Scan type: " + scan_type)
    logging.info("Severities: " + ", ".join(s.value for s in severities))

    # run the scan
    filename = compliance_scan(codedx_project, target_url, scan_type)

    cdx = get_codedx_client()
    codedx_upload(cdx, codedx_project, filename)

    gcs_slack_text = ""
    if scan_type == ScanType.UI:
        storage_object_url = upload_gcp(bucket_name, scan_type, filename)
        gcs_slack_text = (
            f"New vulnerability report uploaded to GCS bucket: {storage_object_url}\n"
        )

    if not slack_channel:
        return

    slack = SlackClient(token=os.environ["SLACK_TOKEN"])

    # send a Slack alert
    if get_codedx_alert_count_by_severity(cdx, codedx_project, severities):
        report_file = get_codedx_report_by_alert_severity(
            cdx, codedx_project, severities
        )
        alerts_string = get_alerts_string(cdx, codedx_project, severities)
        report_message = (
            f"{ gcs_slack_text }"
            f"Endpoint { target_url } contains:\n"
            f"{ alerts_string }"
            f"Please see attached report for details."
        )
        slack.files_upload(
            channels=slack_channel,
            file=report_file,
            title=report_file,
            initial_comment=report_message,
        )
    elif gcs_slack_text:
        slack.chat_postMessage(channel=slack_channel, text=gcs_slack_text)
    else:
        logging.info("Nothing to report")
        return
    logging.info(f"Report sent to Slack channel: {slack_channel}")


if __name__ == "__main__":
    main()
