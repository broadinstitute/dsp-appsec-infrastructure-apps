#!/usr/bin/env python3
"""
Runs ZAP scan, uploads results to Code Dx and GCS, and alerts Slack.
"""

import logging
import os
import re
import csv
from datetime import datetime, timedelta
from enum import Enum
from os import getenv
from sys import exit  # pylint: disable=redefined-builtin
from time import sleep
from typing import List
from urllib.parse import urlparse, urlunparse

import defectdojo_apiv2 as defectdojo
import defusedxml.ElementTree as ET
import drive_upload as drivehelper
import google.cloud.logging
from codedx_api.CodeDxAPI import CodeDx  # pylint: disable=import-error
from google.cloud import storage
from slack_sdk.web import WebClient as SlackClient

from zap import ScanType, zap_compliance_scan, zap_shutdown


def fetch_dojo_product_name(defect_dojo, defect_dojo_user, defect_dojo_key, product_id):
    """
    Fetch dojo product name using product_id
    Includes retries as dojo sometimes does not respond.
    """
    dojo = defectdojo.DefectDojoAPIv2(
    defect_dojo, defect_dojo_key, defect_dojo_user, debug=False, timeout=120)
    max_retries = int(getenv("MAX_RETRIES", '6'))
    retry_delay = 30
    for _ in range(max_retries):
        try:
            product = dojo.get_product(product_id=product_id)
            return product.data["name"]
        except Exception: # pylint: disable=broad-except
            logging.info(product.message)
            sleep(retry_delay)
    raise RuntimeError("Maximum retry attempts reached")


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
    return get_codedx_initial_report(cdx, project)

def fetch_dojo_lead_id(dojo, defect_dojo_user):
    #Doing these as individual retries to avoid uploading the same report twice.
    max_retries = int(getenv("MAX_RETRIES", '5'))
    retry_delay = 30
    for _ in range(max_retries):
        try:
            lead_id = dojo.list_users(defect_dojo_user).data["results"][0]["id"]
            return lead_id
        except Exception: # pylint: disable=broad-except
            sleep(retry_delay)
    logging.error("Did not retrieve dojo user ID, upload failed.")
    raise RuntimeError("Maximum retry attempts reached for requesting lead_id")

def defectdojo_upload(product_id: int, zap_filename: str, defect_dojo_key: str, defect_dojo_user: str, defect_dojo: str):  # pylint: disable=line-too-long
    """
    Upload Zap results in DefectDojo product
    """
    dojo = defectdojo.DefectDojoAPIv2(
        defect_dojo, defect_dojo_key, defect_dojo_user, debug=False, timeout=120)

    absolute_path = os.path.abspath(zap_filename)
    date = datetime.today().strftime("%Y%m%d%H:%M")
    lead_id = fetch_dojo_lead_id(dojo, defect_dojo_user)

# The call to create_engagement sometimes fails.
    retry_delay = 20
    max_retries = int(getenv("MAX_RETRIES", '5'))
    for attempt in range(max_retries):
        try:
            engagement=dojo.create_engagement( name=date, product_id=product_id, lead_id=lead_id,
                target_start=datetime.today().strftime("%Y-%m-%d"),
                target_end=datetime.today().strftime("%Y-%m-%d"), status="In Progress",
                active='True',deduplication_on_engagement='False')
            engagement_id=engagement.data["id"]
            break
        except Exception: # pylint: disable=broad-except
            sleep(retry_delay)
            if attempt == max_retries-1:
                raise RuntimeError("Maximum retry attempts reached for closing engagement")

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
    max_retries = int(getenv("MAX_RETRIES", '3'))
    retry_delay = 20
    for _ in range(max_retries):
        try:
            dojo._request('POST','engagements/'+str(engagement_id)+'/close/')
            return
        except Exception: # pylint: disable=broad-except
            sleep(retry_delay)
    raise RuntimeError("Maximum retry attempts reached for closing engagement")

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
        "status": ["new", "unresolved", "reopened", "escalated"],
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

def get_codedx_initial_report(
        cdx: CodeDx, project: str
):
    """
    Generate a PDF report showing all findings that haven't been closed.
    """
    logging.info("Getting PDF report from Codedx project: %s", project)
    report_date = datetime.now()
    report_file = f'{project.replace("-", "_")}_report_{report_date:%Y%m%d}.pdf'
    filters = {
        "status": [2, 3, 4, 5, 6, 10, 9, 1]
    }
    if not cdx.get_project_id(project):
        cdx.create_project(project)
    cdx.get_pdf(
        project,
        summary_mode="detailed",
        details_mode="simple",
        include_result_details=True,
        include_comments=False,
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
        msg = f"The {scan_type.label()} scan of endpoint {target_url} is complete"
        slack.chat_postMessage(channel=channel, text=msg)
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
            "New vulnerability report uploaded to GCS bucket: " +
                f"{xml_report_url}\n and DefectDojo product: {dd}product/{product_id}"
        )
        slack.chat_postMessage(channel=channel, text=gcs_slack_text)
        logging.info("Alert sent to Slack channel for GCS bucket and DefectDojo upload report")
    else:
        gcs_slack_text = (
            "New vulnerability report uploaded to DefectDojo for " +
                f"{target_url}: {dd}product/{product_id}"
        )
        slack.chat_postMessage(channel=channel, text=gcs_slack_text)
        logging.info("Alert sent to Slack channel for DefectDojo upload report")

# match a hash after a hyphen or dot, and only match 8 or 9 characters of hex
URI_HASH_REGEX = re.compile(r"[-\.][a-zA-Z0-9]{8,9}(?![a-fA-F0-9])")

def clean_uri_path(xml_report):
    """
    Remove the changing hash from the path of static resources in zap report.
    """
    tree = ET.parse(xml_report)
    root = tree.getroot()
    #There's a hash in bundled files that is causing flaws to not match
    # this should remove the hash.
    for uri in root.iter('uri'):
        r=urlparse(uri.text)
        r=r._replace(path=URI_HASH_REGEX.sub('', r.path))
        uri.text = urlunparse(r)
    tree.write(xml_report)

def get_codedx_findings_json(cdx,codedx_project):
    """
    Raw report findings_json
    """
    project_id = cdx.get_project_id(codedx_project)
    options = ["descriptor",
               "issue",
               "descriptions",
               "results.active",
               "results.descriptor",
               "results.descriptions",
               "results.metadata",
               "results.variants.with-body",
               "last-comment-action",
               "metadata,"
               "tags",
               "aggregations.tool-summary",
               "triage-time"]
    config = {
                "filter": {
                    "~status": [
                    7
                    ],
                    "globalConfig":{"ignoreArchived":True}
                },
                "pagination":{"perPage":500,"page":1}
                }
    return cdx.get_finding_table(project_id, options, config,  )

def hail_compliance_export(results_json, project_name, cdx_report_filename):
    """
    Helper function to create a CSV file in the POAM format of the current raw findings
    """
    csv_headers = ["status",
                   "ids",
                   "Weakness Name",
                   "Weakness Description",
                   "Weakness Detector Source",
                   "Weakness Source Identifier",
                   "Asset Identifier",
                   "Original Detection Date",
                   "Scheduled Completion Date",
                   "Original Risk Rating"]
    # create the csv line based on the columns above.
    results = []
    for result in results_json:
        result_line = []
        name = result.get("descriptor").get("name")
        status = result.get("statusName")
        result_line.append(status)
        result_line.append(result.get('id'))
        result_line.append(name)
        result_line.append(result.get("descriptions").get("general").get("content"))
        result_line.append(cdx_report_filename)
        result_line.append(result.get("descriptor").get("hierarchy")[0])
        result_line.append(result.get("location").get("path").get("path"))
        result_line.append(result.get("firstSeenOn"))

        severity = result.get("severity").get("key")
        due_date = datetime.strptime(result.get("firstSeenOn"), "%m/%d/%Y")
        if severity == 5:
            due_date = due_date + timedelta(days=14)
        elif severity == 4:
            due_date = due_date + timedelta(days=30)
        elif severity == 3:
            due_date = due_date + timedelta(days=60)
        elif severity == 2:
            due_date = due_date + timedelta(days=180)
        else:
            due_date = None
        result_line.append(due_date)
        result_line.append(result.get("severity").get("name"))

        results.append(result_line)
        
    logging.info("Writing CSV report")
    report_date = datetime.now()
    report_name = f'{project_name.replace("-", "_")}_report_{report_date:%Y%m%d}.csv'
    with open(report_name, "w", newline='') as csvfile:
        report_writer = csv.writer(csvfile, delimiter=',')
        report_writer.writerow(csv_headers)
        for line in results:
            report_writer.writerow(line)
    return report_name
    
def upload_googledrive(scan_type, zap_filename, codedx_project, report_file, slack_token, slack_channel, csv_report_name=None):
    """
    Uploads the xml and initial codedx reports to the appropriate google drive location,
    according to scan type.
    """
    root_id = os.getenv('DRIVE_ROOT_ID', None)
    drive_id = os.getenv('DRIVE_ID', None)
    if scan_type in (ScanType.BASELINE):
        return
    try:
        logging.info('Setting up the google drive API service for uploading reports.')
        if scan_type in (ScanType.HAILAPI, ScanType.HAILAUTH):
            root_id = os.getenv('HAIL_DRIVE_ID')
            drive_id = None

        drive_service = drivehelper.get_drive_service()
        folder_structure = drivehelper.get_folders_with_structure(root_id,
                                                                    drive_id,
                                                                    drive_service)
        if not folder_structure:
            raise RuntimeError("The provided gdrive folder ID was not found.")
        date = datetime.today()
        date = drivehelper.adjust_date(date)
        _, xml_folder_dict, zap_raw_folder = drivehelper.get_upload_folders(folder_structure, date)
        file = drivehelper.upload_file_to_drive(zap_filename,
                                                    xml_folder_dict.get('id'),
                                                    drive_id,
                                                    drive_service)
        logging.info(f"The returned file id for {codedx_project} XML is {file}")
        if not file:
            raise RuntimeError(f"The XML file for {codedx_project} was not uploaded to {xml_folder_dict.get('id')}.")
        file2 = drivehelper.upload_file_to_drive(report_file,
                                                    zap_raw_folder.get('id'),
                                                    drive_id,
                                                    drive_service)
        if not file2:
            raise RuntimeError(
                        f"The CodeDx report for {codedx_project} was not uploaded to {zap_raw_folder.get('id')}.")
        logging.info(f"The returned file id for {codedx_project} Raw Report is {file2}")
        logging.info(f'The report {report_file} has been uploaded.')
        if scan_type in (ScanType.HAILAPI, ScanType.HAILAUTH):
            # export the raw report in a format that can be used to generate POAMs
            
            file3 = drivehelper.upload_file_to_drive(csv_report_name,
                                                        zap_raw_folder.get('id'),
                                                        drive_id,
                                                        drive_service)
            if not file3:
                raise RuntimeError(
                    f"The raw report csv for {codedx_project} was not uploaded to {zap_raw_folder.get('id')}.")
            logging.info(f"The returned file id for {codedx_project} CSV report is {file3}")
 
    except Exception as e: # pylint: disable=broad-except
        error_message = f'Failed to complete uploading files to GDrive for {codedx_project}. Last error {e}'
        logging.info(error_message)
        error_slack_alert(
            error_message, slack_token, slack_channel)


def main(): # pylint: disable=too-many-locals
    """
    - Run ZAP scan
    - Upload results to Code Dx
    - Upload ZAP XML report to GCS, if needed
    - Send a Slack alert with Code Dx report, if needed.
    """
    client = google.cloud.logging.Client()
    client.setup_logging()

    max_retries = int(getenv("MAX_RETRIES", '1'))
    sleep_time = 10
    for attempt in range(max_retries):
        # run Zap scan
        try:
            # parse env variables
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
            # configure logging
            logging.basicConfig(level=logging.INFO,
                format=f"%(levelname)-8s [{codedx_project} {scan_type}-scan] %(message)s",
                )
            # fetch dd poject name
            dojo_product_name = fetch_dojo_product_name(defect_dojo,
                                                            defect_dojo_user,
                                                            defect_dojo_key,
                                                            product_id)

            logging.info("Severities: %s", ", ".join(
                s.value for s in severities))

            (zap_filename, session_filename) = zap_compliance_scan(
                dojo_product_name, target_url, scan_type)

            # optionally, upload them to GCS
            xml_report_url = ""
            if scan_type is not ScanType.BASELINE:
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
            if scan_type in (ScanType.UI, ScanType.LEOAPP, ScanType.BEEHIVE):
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
                zap_shutdown()
                return

            # upload its results to Code Dx
            cdx = CodeDx(codedx_url, codedx_api_key)

            cdx_filename = codedx_upload(cdx, codedx_project, zap_filename)

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

            report_name = None
            # Upload Terra scan XMLs and CodeDx reports to Google Drive.
            logging.info("ready to upload to google drive")
            if scan_type in (ScanType.HAILAPI, ScanType.HAILAUTH):
                logging.info("Pulling findings JSON for hail to build report CSV.")
                findings_json = get_codedx_findings_json(cdx, codedx_project)
                report_name = hail_compliance_export(findings_json, codedx_project, cdx_filename)


            upload_googledrive(scan_type, zap_filename, codedx_project, cdx_filename, slack_token, slack_channel, report_name)

            zap_shutdown()
            return
        except Exception as error: # pylint: disable=broad-except
            error_message = f"[RETRY-{ attempt }] Exception running Zap Scans: { error }"
            logging.warning(error_message)
            if attempt == max_retries - 1:
                error_message = f"Error running Zap Scans for { target_url }. Last error: { error }"
                try:
                    error_slack_alert(error_message, slack_token, slack_channel)
                except:
                    logging.error(f"Slack could not post to {slack_channel}")
                try:
                    zap_shutdown()
                except Exception as zap_e: # pylint: disable=broad-except
                    error_message = f"Error shutting down zap: { zap_e }"
                    error_slack_alert(
                        error_message, slack_token, slack_channel)
                    logging.exception("Error shutting down zap.")
                logging.exception("Max retries exceeded.")
                exit(0)
            sleep(sleep_time)
            sleep_time *= 2
        else:
            break


if __name__ == "__main__":
    main()
