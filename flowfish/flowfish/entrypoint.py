#!/usr/bin/env python3

import json
import os
import subprocess
import xml.etree.ElementTree as etree
import requests
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


gcp_project_id = os.getenv('GCP_PROJECT_ID')
targets = os.getenv('TARGET')
bigquery_table = os.getenv('BQ_TABLE')
bigquery_dataset = os.getenv('BQ_DATASET')
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
scan_report = "scan_report.xml"


def scan() -> json:
    """
    Runs a scan
    """
    # ToDo:  Need to check whether single target or multiple ones
    # through file input
    args = f'''
        nmap -sV --script nmap-vulners  -oX {scan_report} -sV {targets}
    '''.split()
    p = subprocess.run(args, capture_output=True, text=True)
    res = parse_raw(scan_report)
    load_bigquery(res)


def parse_raw(raw_output: str) -> json:
    """Parse raw xml output from nmap
    Arguments:
        raw_output name {str} -- [nmap xml report -oX]
    Returns:
        json -- [description]
    """
    doc = etree.parse(raw_output)
    cves = {}

    for host in doc.iterfind('host'):
        hostname = host.find('hostnames/*[1]')
        if hostname is None:
            continue
        hostname = hostname.get('name')
        for port in host.iterfind('ports/port'):
            port_id = port.get('portid')
            if not port_id:
                continue
            for vuln in port.iterfind('script/table/table'):
                cve = {}
                for elem in vuln.iterfind('elem'):
                    key = elem.get('key')
                    if not key:
                        continue
                    cve[key] = elem.text
                if 'type' in cve and cve['type'] == 'cve':
                    cve_id = cve['id']
                    if cve_id not in cves:
                        cves[cve_id] = {
                            'cvss': cve['cvss'],
                            'targets': [],
                        }
                    cves[cve_id]['targets'].append(f'{hostname}:{port_id}')

    parsed = (json.dumps(cves, indent=2))
    return parsed


def load_bigquery(json_results) -> None:
    """Load results to BigQuery
    Arguments:
        json_results {json dump} -- [deduplicated json issues]
    """
    bq = bigquery.Client()
    try:
        table = bq.get_table(bigquery_table)
    except NotFound:
        field = bigquery.SchemaField
        table = bigquery.Table(bigquery_table, schema=[
            field("CVE", "STRING"),
            field("CVSS", "STRING"),
            field("TARGET_DNS", "STRING"),
        ])

        table = bq.create_table(table)

    rows = []

    data = json.loads(json_results)
    print(f"Data, {type(data)}")

    for item in data:
        cve = item
        cvss = data[item]['cvss']
        targets = data[item]["targets"]
        for target_dns in targets:
            rows.append({
                "CVE": cve,
                "CVSS": cvss,
                "TARGET_DNS": target_dns
            })

    errors = bq.insert_rows(table, rows)
    if errors:
        print(errors)


def slack_notify(slack_webhook_url: str) -> None:
    """
    Send slack webhook notification when new scan 
    is initiated

    Arguments:
        slack_channel {str} -- [Slack Webhook URL]
    """
    data = {
        'text': 'New Vulnerability Scan initiated',
        'icon_emoji': ':robot_face:'
    }
    try:
        response = requests.post(slack_webhook_url, data=json.dumps(
            data), headers={'Content-Type': 'application/json'})
        print(response)
    except Exception as e:
        print(f"Slack notify error: {e}")


def main():
    scan()


if __name__ == '__main__':
    main()
