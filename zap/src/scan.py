#!/usr/bin/env python3
"""
Runs ZAP scan, uploads results to Code Dx and GCS, and alerts Slack.
"""

import logging
import os
import re
from datetime import datetime
from enum import Enum
from os import getenv
from sys import exit  # pylint: disable=redefined-builtin
from time import sleep
from typing import List
from urllib.parse import urlparse, urlunparse

import defectdojo_apiv2 as defectdojo
import defusedxml.ElementTree as ET
from codedx_api.CodeDxAPI import CodeDx  # pylint: disable=import-error
from google.cloud import storage
from slack_sdk.web import WebClient as SlackClient

from zap import ScanType, zap_compliance_scan, zap_connect


def fetch_dojo_product_name(defect_dojo, defect_dojo_user, defect_dojo_key, product_id):
    """
    Fetch dojo product name using product_id
    """
    dojo = defectdojo.DefectDojoAPIv2(
        defect_dojo, defect_dojo_key, defect_dojo_user, debug=False, timeout=120)
    product = dojo.get_product(product_id=product_id)
    return product["name"]

def upload_gcs(bucket_name: str, scan_type: ScanType, filename: str, subfoldername=None):
    """
    Upload scans to a GCS bucket and return the path to the file in Cloud Console.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    date = datetime.today().strftime("%Y%m%d")
    if subfoldername is None:
        path = f"{scan_type}-scans/{date}/{filename}"
    else:
        path = f"{scan_type}-scans/{date}/{subfoldername}/{filename}"
    blob = bucket.blob(path)
    blob.upload_from_filename(filename)
    return f"https://console.cloud.google.com/storage/browser/_details/{bucket_name}/{path}"        

def error_slack_alert(error: str, token: str, channel: str):
    """
    Send error to slack or make a note in the logs.
    """
    if not channel:
        error_log = f"{ error }. No Slack alert requested."
        logging.warning(error_log)
    else:
        slack = SlackClient(token)
        slack.chat_postMessage(channel=channel, text=error)


def codedx_upload(cdx: CodeDx, project: str, filename: str):
    """
    Create CodeDx project if needed and trigger analysis on the uploaded file.
    """
    if not cdx.get_project_id(project):
        cdx.create_project(project)

    cdx.analyze(project, filename)


def defectdojo_upload(product_id: int, zap_filename: str, defect_dojo_key: str, defect_dojo_user: str, defect_dojo: str):  # pylint: disable=line-too-long
    """
    Upload Zap results in DefectDojo product
    """
    dojo = defectdojo.DefectDojoAPIv2(
        defect_dojo, defect_dojo_key, defect_dojo_user, debug=False, timeout=120)

    absolute_path = os.path.abspath(zap_filename)
    date = datetime.today().strftime("%Y%m%d%H:%M")
    
    try:
        lead_id = dojo.list_users(defect_dojo_user).data["results"][0]["id"]
    except Exception:
        logging.error("Did not retrieve dojo user ID, upload failed.")
        return

    engagement=dojo.create_engagement( name=date, product_id=product_id, lead_id=lead_id,
        target_start=datetime.today().strftime("%Y-%m-%d"),
        target_end=datetime.today().strftime("%Y-%m-%d"), status="In Progress",
        active='True',deduplication_on_engagement='False')
    print(engagement.data)
    engagement_id=engagement.data["id"]

    dojo_upload = dojo.upload_scan(engagement_id=engagement_id,
                     scan_type="ZAP Scan",
                     file=absolute_path,
                     active=True,
                     verified=False,
                     close_old_findings=True,
                     skip_duplicates=True,
                     scan_date=str(datetime.today().strftime('%Y-%m-%d')),
                     tags="Zap_scan")
    logging.info("Dojo file upload: %s", dojo_upload)
    dojo._request('POST','engagements/'+str(engagement_id)+'/close/')

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
        cdx: CodeDx,
        project: str,
        severities: List[Severity]
) -> int:
    """
    Get finding count, given the severity levels for a Code Dx project.
    """
    filters = {
        "filter": {
            "severity": [s.value for s in severities],
            "status": ["new", "unresolved", "reopened"],
        },
    }
    pid = cdx.get_project_id(project)
    if not pid:
        new_project = cdx.create_project(project)
        pid = new_project["id"]
    res = cdx.get_finding_count(pid, filters)
    if "count" not in res:
        raise RuntimeError(f"{ res }")

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
    if not cdx.get_project_id(project):
        cdx.create_project(project)
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
            f"Results from {scan_type.label()} scan of endpoint { target_url }:\n"
            f"{ alerts_string }"
            f"Please see the attached report for details."
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
    logging.info("Alert sent to Slack channel")


def slack_alert_without_report(  # pylint: disable=too-many-arguments
        token: str,
        channel: str,
        xml_report_url: str,
        product_id: str,
        dd: str,
        target_url: str
):
    """
    Alert Slack on requested findings, if any.
    """
    # continue only if Slack channel is set
    if not channel:
        logging.warning("Slack alert was not requested")
        return

    slack = SlackClient(token)

    if xml_report_url:
        gcs_slack_text = (
            f"New vulnerability report uploaded to GCS bucket: {xml_report_url}\n and DefectDojo product: {dd}product/{product_id}"
        )
        slack.chat_postMessage(channel=channel, text=gcs_slack_text)
        logging.info("Alert sent to Slack channel for GCS bucket and DefectDojo upload report")
    else:
        gcs_slack_text = (
            f"New vulnerability report uploaded to DefectDojo for {target_url}: {dd}product/{product_id}"
        )
        slack.chat_postMessage(channel=channel, text=gcs_slack_text)
        logging.info("Alert sent to Slack channel for DefectDojo upload report")

def clean_uri_path(xml_report):
    """
    Remove the changing hash from the path of static resources in zap report.
    """
    tree = ET.parse(xml_report)
    root = tree.getroot()
    #There's a hash in bundled files that is causing flaws to not match, this should remove the hash.
    for uri in root.iter('uri'):
        r=urlparse(uri.text)
        r=r._replace(path=re.sub('\.([a-zA-Z0-9]+){8,9}', '', r.path))
        uri.text = urlunparse(r)
    tree.write(xml_report)


def main(): # pylint: disable=too-many-locals
    """
    - Run ZAP scan
    - Upload results to Code Dx
    - Upload ZAP XML report to GCS, if needed
    - Send a Slack alert with Code Dx report, if needed.
    """
    max_retries = int(getenv("MAX_RETRIES", '1'))

    for attempt in range(max_retries):
        # run Zap scan
        try:
            # parse env variables
            zap_port = int(getenv("ZAP_PORT", ""))

            codedx_project = getenv("CODEDX_PROJECT")
            codedx_url = getenv("CODEDX_URL")
            codedx_api_key = getenv("CODEDX_API_KEY")

            target_url = getenv("URL")
            scan_type = ScanType[getenv("SCAN_TYPE").upper()]

            bucket_name = getenv("BUCKET_NAME")
            session_bucket = getenv("SESSION_BUCKET")

            slack_channel = getenv("SLACK_CHANNEL")
            slack_token = getenv("SLACK_TOKEN")

            severities = parse_severities(getenv("SEVERITIES"))

            # variables needed for DefectDojo
            defect_dojo_key = getenv("DEFECT_DOJO_KEY")
            product_id = int(getenv("PRODUCT_ID"))
            defect_dojo_user = getenv("DEFECT_DOJO_USER")
            defect_dojo = getenv("DEFECT_DOJO_URL")
            dd = getenv("DEFECT_DOJO")

            # fetch dd poject name
            dojo_product_name = fetch_dojo_product_name(defect_dojo, defect_dojo_user, defect_dojo_key, product_id)


            # configure logging
            logging.basicConfig(level=logging.INFO,
                format=f"%(levelname)-8s [{codedx_project} {scan_type}-scan] %(message)s",
                )

            logging.info("Severities: %s", ", ".join(
                s.value for s in severities))

            (zap_filename, session_filename) = zap_compliance_scan(
                dojo_product_name, zap_port, target_url, scan_type)

            # optionally, upload them to GCS
            xml_report_url = ""
            if scan_type == ScanType.UI:
                xml_report_url = upload_gcs(
                    bucket_name,
                    scan_type,
                    zap_filename,
                    subfoldername='raw'
                )
                upload_gcs(
                    session_bucket,
                    scan_type,
                    session_filename,
                )

            #removes hash from certain static files to improve flaw matching.
            #done after upload of raw report to GCS to preserve raw report xml.
            clean_uri_path(zap_filename)

            #upload scrubbed results in case we need to do a manual upload
            if scan_type == ScanType.UI:
                xml_report_url = upload_gcs(
                    bucket_name,
                    scan_type,
                    zap_filename,
                    subfoldername='clean'
                )

            # upload its results in defectDojo
            defectdojo_upload(product_id, zap_filename,
                              defect_dojo_key, defect_dojo_user, defect_dojo)

            
            if codedx_api_key == '""' or codedx_project == '':
                slack_alert_without_report(
                    slack_token,
                    slack_channel,
                    xml_report_url,
                    product_id,
                    dd,
                    target_url
                )
            else:
                # upload its results to Code Dx
                cdx = CodeDx(codedx_url, codedx_api_key)

                codedx_upload(cdx, codedx_project, zap_filename)

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


            zap = zap_connect(zap_port)
            zap.core.shutdown()
        except Exception as error: # pylint: disable=broad-except
            error_message = f"[RETRY-{ attempt }] Exception running Zap Scans: { error }"
            logging.warning(error_message)
            if attempt == max_retries - 1:
                error_message = f"Error running Zap Scans for { target_url }. Last known error: { error }"
                error_slack_alert(error_message, slack_token, slack_channel)
                try:
                    zap = zap_connect(zap_port)
                    zap.core.shutdown()
                except Exception as zap_e: # pylint: disable=broad-except
                    error_message = f"Error shutting down zap: { zap_e }"
                    error_slack_alert(
                        error_message, slack_token, slack_channel)
                    logging.exception("Error shutting down zap.")
                logging.exception("Max retries exceeded.")
                exit(0)
            sleep(5)
        else:
            break


if __name__ == "__main__":
    main()
