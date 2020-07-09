#!/usr/bin/env python3
"""
This module
- scans a GCP project with Inspec GCP CIS Benchmark
- records results into a BigQuery table
- optionally notifies a Slack channel about results
- optionally records completion in a Firestore doc
"""

import json
import logging
import os
import subprocess
from typing import Any, List

import slack
from google.cloud import bigquery, firestore, resource_manager

BENCHMARK_PROFILE = 'inspec-gcp-cis-benchmark'


def benchmark(target_project_id: str):
    """
    Runs Inspec GCP CIS benchmark on `target_project_id`,
    and returns the parsed results.
    """
    logging.info("Running %s for %s", BENCHMARK_PROFILE, target_project_id)
    proc = subprocess.run([
        'inspec', 'exec', 'inspec-gcp-cis-benchmark',
        '-t', 'gcp://', '--reporter', 'json',
        '--input', f'gcp_project_id={target_project_id}',
    ], capture_output=True, text=True, check=False)

    # normal exit codes as documented at
    # https://www.inspec.io/docs/reference/cli
    if proc.returncode not in (0, 100, 101):
        logging.error(proc.stderr)
        raise subprocess.CalledProcessError(proc.returncode, proc.args)

    for out in proc.stdout.splitlines():
        if out.startswith('{'):
            return target_project_id, json.loads(out)['profiles']
    return None


def parse_profiles(target_project_id: str, profiles):
    """
    Parses scan results into a table structure for BigQuery.
    """
    profile = None
    version: str = ''
    for prof in profiles:
        if prof['name'] == 'inspec-gcp':
            version = prof['version']
        elif prof['name'] == BENCHMARK_PROFILE:
            profile = prof
    if not profile or not version:
        raise ValueError(
            'Unable to determine profile or version from scan results')

    title: str = profile['title']
    rows = []
    for ctrl in profile['controls']:
        failures = []
        for res in ctrl['results']:
            if res['status'] != 'failed' or 'exception' in res:
                continue
            failures.append(
                res['code_desc']
                .replace(f'[{target_project_id}] ', '', 1)
                .replace('cmp == nil', 'be empty')
                .replace('cmp ==', 'equal')
            )
        if not failures:
            continue

        rationale = ''
        for desc in ctrl['descriptions']:
            if desc['label'] != 'rationale':
                continue
            rationale = desc['data']

        tags = ctrl['tags']
        refs = collect_refs(ctrl['refs'], [])

        rows.append({
            'id': tags['cis_gcp'],
            'level': tags['cis_level'],
            'impact': str(ctrl['impact']),
            'title': ctrl['title'],
            'failures': failures,
            'description': ctrl['desc'],
            'rationale': rationale,
            'refs': refs,
        })

    return title, version, rows


def collect_refs(refs: list, urls: List[str]):
    """
    Recursively collects reference URLs.
    """
    for ref in refs:
        if 'url' in ref:
            urls.append(ref['url'])
        if 'ref' in ref and isinstance(ref['ref'], list):
            collect_refs(ref['ref'], urls)
    return urls


def load_bigquery(target_project_id: str, dataset_id: str, table_desc: str, version: str, rows: List[Any]):
    """
    Loads scan results into a BigQuery table.
    """
    table_id = target_project_id.replace('-', '_')

    if not rows:
        return table_id

    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)

    f = bigquery.SchemaField
    schema = (
        f('id', 'STRING', mode='REQUIRED'),
        f('level', 'INTEGER', mode='REQUIRED'),
        f('impact', 'STRING', mode='REQUIRED'),
        f('title', 'STRING', mode='REQUIRED'),
        f('failures', 'STRING', mode='REPEATED'),
        f('description', 'STRING', mode='REQUIRED'),
        f('rationale', 'STRING', mode='REQUIRED'),
        f('refs', 'STRING', mode='REPEATED'),
    )
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
        ),
        labels={
            'gcp-project': target_project_id,
            'inspec-version': version.replace('.', '_'),
        },
    )

    job = client.load_table_from_json(rows, table_ref, job_config=job_config)
    job.result()  # wait for completion
    logging.info("Loaded %s rows into %s.%s",
                 job.output_rows, dataset_id, table_id)

    # update table description
    table = bigquery.Table(table_ref)
    table.description = table_desc
    client.update_table(table, ['description'])

    return table_id


def firestore_report(collection_id: str, table_id: str):
    """
    Records scan completion into a Firestore document.
    """
    client = firestore.Client()
    doc_ref = client.collection(collection_id).document(table_id)
    doc_ref.set({})


def slack_notify(target_project_id: str, slack_token: str, slack_channel: str, results_url: str):
    """
    Posts a notification about results to Slack.
    """
    client = slack.WebClient(slack_token)
    client.chat_postMessage(
        channel=slack_channel,
        attachments=[{"blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Check `{0}` CIS scan results :spiral_note_pad:" .format(target_project_id)
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Get results"
                        },
                        "url": results_url,
                    }
                ]
            }], "color": "#0731b0"}]
    )


def find_highs(rows: List[Any], slack_channel: str, slack_token: str, target_project_id: str):
    """
    Find high vulnerabilities from GCP project scan.

    Args:
       List of project findings, slack channel, slack token
    Returns:
        None
    """
    records = []
    for row in rows:
        if float(row['impact']) > 0.6:
            records.append({
                'impact': row['impact'],
                'title': row['title'],
                'description': row['description']
            })
    if records:
        slack_notify_high(records, slack_token, slack_channel, target_project_id)


def slack_notify_high(records: List[Any], slack_token: str, slack_channel: str, target_project_id: str):
    """
    Post notifications in Slack
    about high findings
    """
    client = slack.WebClient(slack_token)
    for row in records:
        client.chat_postMessage(
            channel=slack_channel,
            attachments=[{"blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "* | High finding in  `{0}` GCP project* :gcpcloud: :" .format(target_project_id)
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Impact*: `{0}`" .format(str(float(row['impact'])*10))

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Title*: `{0}`" .format(row['title'])

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Description* `{0}`" .format(row['description'])

                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "image",
                            "image_url":
                            "https://platform.slack-edge.com/img/default_application_icon.png",
                            "alt_text": "slack"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*GCP* Project Weekly Scan"
                        }
                    ]
                }
            ],
                          "color": "#C31818"}]
        )


def validate_project(target_project_id: str):
    """
    Checks if GCP `project_id` exists via Resource Manager API.
    Raises a NotFound error if not.
    """
    client = resource_manager.Client()
    client.fetch_project(target_project_id)


def main():
    """
    Implements the entrypoint.
    """
    # configure logging
    logging.basicConfig(level=logging.INFO)

    # parse inputs
    target_project_id = os.environ['TARGET_PROJECT_ID'] # required
    dataset_id = os.environ['BQ_DATASET']  # required
    slack_token = os.getenv('SLACK_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL') # slack channel if provided from user
    slack_results_url = os.getenv('SLACK_RESULTS_URL')
    fs_collection = os.getenv('FIRESTORE_COLLECTION')

    try:
        # validate inputs
        validate_project(target_project_id)

        # scan and load results into BigQuery
        title, version, rows = parse_profiles(*benchmark(target_project_id))
        table_id = load_bigquery(target_project_id, dataset_id, title, version, rows)

        # post to Slack, if specified
        if slack_token and slack_channel and slack_results_url:
            slack_notify(target_project_id, slack_token, slack_channel, slack_results_url)
            find_highs(rows, slack_channel, slack_token, target_project_id)
        # create Firestore document, if specified
        if fs_collection:
            firestore_report(fs_collection, table_id)

    # writes an error in Firestore document if an exception occurs
    except (Exception) as error:
        client = firestore.Client()
        doc_ref = client.collection(fs_collection).document(table_id)
        doc_ref.set({u'Error': u'{}'.format(error)})
        print(Exception)
        raise error

if __name__ == '__main__':
    main()
