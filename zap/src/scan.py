#!/usr/bin/env python3

import logging
import os
from datetime import datetime

from codedx_api import CodeDxAPI
from google.cloud import storage

from notify import slack_message, slack_attach
from zap import compliance_scan


def upload_gcp(bucket_name, scan, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    date = datetime.today().strftime('%Y%m%d')
    path = f'{scan}s/{date}/{filename}'
    blob = bucket.blob(path)
    blob.upload_from_filename(filename)
    location = f"https://console.cloud.google.com/storage/browser/_details/{bucket_name}/{path}"
    return location


def get_codedx_client():
    base_url = os.getenv('CODEDX_URL')
    codedx_api_key = os.getenv('CODEDX_API_KEY')
    cdx = CodeDxAPI.CodeDx(base_url, codedx_api_key)
    return cdx


def codedx_upload(project, file_name):
    cdx = get_codedx_client()
    cdx.update_projects()

    if project not in list(cdx.projects):
        cdx.create_project(project)

    cdx.analyze(project, file_name)


def get_codedx_alert_count_by_severity(project, alert_filters):
    cdx = get_codedx_client()
    cdx.update_projects()
    if project not in list(cdx.projects):
        print("Error getting high alert count: project does not exist.")
        return
    filters = {
                "filter": {
                    "severity": alert_filters
                }
            }
    res = cdx.get_finding_count(project, filters)
    if "count" not in res:
        print(f"Error fetching count: {res}")
    return res["count"]


def get_alerts_string(codedx_project, alert_filters):
    alert_string = ""
    emojis = {
        "Critical": ":stopsign:",
        "High": ":triangular_flag_on_post:",
        "Medium": ":radioactive_sign:",
        "Low": ":warning:",
        "Info": ":heavy_check_mark:"
    }
    for severity in alert_filters:
        count = get_codedx_alert_count_by_severity(codedx_project, severity)
        alert_string += f"\t{ emojis[severity] } { count } { severity } findings\n"
    return alert_string


def get_codedx_report_by_alert_severity(project, severity_filters):
    print(f"Getting PDF report from Codedx project: {project}")
    cdx = get_codedx_client()
    cdx.update_projects()
    if project not in list(cdx.projects):
        print("Error getting PDF report: project does not exist for PDF report.")
        return
    report_date = datetime.now()
    report_title = f'{project.replace("-", "_")}_report_{report_date:%Y%m%d}.pdf'
    filters = {
        "severity": severity_filters,
        "status": ["new", "unresolved", "reopened"]
    }
    cdx.get_pdf(project,
                summary_mode="detailed",
                details_mode="with-source",
                include_result_details=True,
                include_comments=True,
                include_request_response=False,
                file_name=report_title,
                filters=filters)

    return report_title


def main():
    # configure logging
    logging.basicConfig(level=logging.INFO)
    # get scan variables
    codedx_project = os.getenv('CODEDX_PROJECT')
    target_url = os.getenv('URL')
    scan_type = os.getenv('SCAN_TYPE')
    bucket_name = os.getenv('BUCKET_NAME')
    slack_channel = os.getenv('SLACK_CHANNEL')
    all_alerts = os.getenv('ALL_ALERTS')

    if all_alerts:
        alert_filters = ["Critical", "High", "Medium", "Low", "Info"]
    else:
        alert_filters = ["Critical", "High"]

    # run the scan
    filename = compliance_scan(codedx_project, target_url, scan_type)
    codedx_upload(codedx_project, filename)

    gcs_slack_text = ""
    if scan_type == "ui-scan":
        # if no slack_channel given, send alerts on ui-scans to defaults AppSec channel
        storage_object_url = upload_gcp(bucket_name, scan_type, filename)
        gcs_slack_text = f"New vulnerability report uploaded to GCS bucket: {storage_object_url}\n"

    # upload to codedx
    if slack_channel:
        alert_count = get_codedx_alert_count_by_severity(codedx_project, alert_filters)
        if alert_count > 0:
            report = get_codedx_report_by_alert_severity(codedx_project, alert_filters)
            alerts_string = get_alerts_string(codedx_project, alert_filters)
            report_message = (
                f"{ gcs_slack_text }"
                f"Endpoint { target_url } contains:\n"
                f"{ alerts_string }"
                f"Please see attached report for details."
            )
            slack_attach(slack_channel, report_message, report)
        elif gcs_slack_text:
            slack_message(slack_channel, gcs_slack_text)


if __name__ == "__main__":
    main()
