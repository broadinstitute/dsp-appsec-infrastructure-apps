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
import re
import subprocess
import sys
from typing import Any, List

import slack
from google.cloud import bigquery, firestore, resource_manager

BENCHMARK_PROFILES = (
    'inspec-gcp-cis-benchmark',
    'inspec-gke-cis-gcp',
    'inspec-gke-cis-k8s',
)


def benchmark(target_project_id: str, profile: str):
    """
    Runs a Google Cloud Inspec CIS benchmark profile
    on `target_project_id`, and returns the parsed results.
    """
    logging.info("Running %s for %s", profile, target_project_id)
    proc = subprocess.run([
        'inspec', 'exec', profile,
        '-t', 'gcp://', '--reporter', 'json',
        '--input', f'gcp_project_id={target_project_id}',
    ], stdout=subprocess.PIPE, stderr=sys.stderr, text=True, check=False)

    # normal exit codes as documented at
    # https://www.inspec.io/docs/reference/cli
    if proc.returncode not in (0, 100, 101):
        raise subprocess.CalledProcessError(proc.returncode, proc.args)

    for out in proc.stdout.splitlines():
        if out.startswith('{'):
            return json.loads(out)['profiles']
    return None


def benchmarks(target_project_id: str):
    """
    Runs GCP and GKE benchmarks on `target_project_id`,
    and returns the parsed results.
    """
    profiles = []
    for profile in BENCHMARK_PROFILES:
        profiles.extend(benchmark(target_project_id, profile))
    return target_project_id, profiles


def parse_profiles(target_project_id: str, profiles):
    """
    Parses scan results into a table structure for BigQuery.
    """
    rows: List[Any] = []
    titles: List[str] = []
    for profile in profiles:
        if profile['name'] not in BENCHMARK_PROFILES:
            continue

        titles.append(profile['title'])
        for ctrl in profile['controls']:
            failures = []
            for res in ctrl['results']:
                if 'exception' in res:
                    logging.error(res['code_desc'] + ': ' + res['message'])
                    continue
                if res['status'] != 'failed':
                    continue
                failures.append(
                    re.sub(f'\\[{target_project_id}( , )?(.*) ?\\] ',
                           r'\2', res['code_desc'])
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
            tag_id = '_'.join(profile['name'].split('-')[2:0:-1])
            refs = collect_refs(ctrl['refs'], [])

            rows.append({
                'id': tags[tag_id],
                'level': tags['cis_level'],
                'impact': str(ctrl['impact']),
                'title': ctrl['title'],
                'failures': failures,
                'description': ctrl['desc'],
                'rationale': rationale,
                'refs': refs,
            })

    return '; '.join(titles), rows


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


def load_bigquery(target_project_id: str, dataset_id: str, table_id: str,
                  table_desc: str, rows: List[Any]):
    """
    Loads scan results into a BigQuery table.
    """
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
                    "text": f"Check `{target_project_id}` CIS scan results :spiral_note_pad:",
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
        slack_notify_high(records, slack_token,
                          slack_channel, target_project_id)


def slack_notify_high(records: List[Any], slack_token: str,
                      slack_channel: str, target_project_id: str):
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
                        "text":
                            f"* | High finding in `{target_project_id}` GCP project* :gcpcloud: :",
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Impact*: `{float(row['impact'])*10}`",

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Title*: `{row['title']}`",

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description* `{row['description']}`",

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
            ], "color": "#C31818"}]
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
    target_project_id = os.environ['TARGET_PROJECT_ID']  # required
    dataset_id = os.environ['BQ_DATASET']  # required
    slack_token = os.getenv('SLACK_TOKEN')
    # slack channel if provided from user
    slack_channel = os.getenv('SLACK_CHANNEL')
    slack_results_url = os.getenv('SLACK_RESULTS_URL')
    fs_collection = os.getenv('FIRESTORE_COLLECTION')

    try:
        # define table_id and Firestore doc_ref for reporting success/errors
        table_id = target_project_id.replace('-', '_')
        if fs_collection:
            doc_ref = firestore.Client().collection(fs_collection).document(table_id)

        # validate inputs
        validate_project(target_project_id)

        # scan and load results into BigQuery
        title, rows = parse_profiles(*benchmarks(target_project_id))
        load_bigquery(target_project_id, dataset_id, table_id, title, rows)

        # post to Slack, if specified
        if slack_token and slack_channel and slack_results_url:
            slack_notify(target_project_id, slack_token,
                         slack_channel, slack_results_url)
            find_highs(rows, slack_channel, slack_token, target_project_id)
        # create Firestore document, if specified

        if fs_collection:
            doc_ref.set({})

    # writes an error in Firestore document if an exception occurs
    except (Exception) as error:
        if fs_collection:
            doc_ref.set({u'Error': u'{}'.format(error)})
        raise error


if __name__ == '__main__':
    main()
