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
from typing import List, Any
import slack

from google.cloud import bigquery, firestore, resource_manager


BENCHMARK_PROFILE = 'inspec-gcp-cis-benchmark'


def benchmark(project_id: str):
    """
    Runs Inspec GCP CIS benchmark on `project_id`,
    and returns the parsed results.
    """
    logging.info("Running %s for %s", BENCHMARK_PROFILE, project_id)
    proc = subprocess.run([
        'inspec', 'exec', 'inspec-gcp-cis-benchmark',
        '-t', 'gcp://', '--reporter', 'json',
        '--input', f'gcp_project_id={project_id}',
    ], capture_output=True, text=True, check=False)

    # normal exit codes as documented at
    # https://www.inspec.io/docs/reference/cli
    if proc.returncode not in (0, 100, 101):
        logging.error(proc.stderr)
        raise subprocess.CalledProcessError(proc.returncode, proc.args)

    return project_id, json.loads(proc.stdout)['profiles']


def parse_profiles(project_id: str, profiles):
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
                .replace(f'[{project_id}] ', '', 1)
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
        refs = [ref['url'] for ref in ctrl['refs']]

        rows.append({
            'id': tags['cis_gcp'],
            'level': tags['cis_level'],
            'title': ctrl['title'],
            'failures': failures,
            'description': ctrl['desc'],
            'rationale': rationale,
            'refs': refs,
        })

    return title, version, rows


def load_bigquery(project_id: str, dataset_id: str, table_desc: str, version: str, rows: List[Any]):
    """
    Loads scan results into a BigQuery table.
    """
    table_id = project_id.replace('-', '_')

    if not rows:
        return table_id

    client = bigquery.Client()
    table = client.dataset(dataset_id).table(table_id)

    f = bigquery.SchemaField
    schema = (
        f('id', 'STRING', mode='REQUIRED'),
        f('level', 'INTEGER', mode='REQUIRED'),
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
            'gcp-project': project_id,
            'inspec-version': version.replace('.', '_'),
        },
    )

    job = client.load_table_from_json(rows, table, job_config=job_config)
    job.result()  # wait for completion
    logging.info("Loaded %s rows into %s.%s",
                 job.output_rows, dataset_id, table_id)

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


def slack_notify(project_id: str, slack_token: str, slack_channel: str, results_url: str):
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
                    "text": "Check `{0}` CIS scan results :spiral_note_pad:" .format(project_id)
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


def validate_project(project_id: str):
    """
    Checks if GCP `project_id` exists via Resource Manager API.
    Raises a NotFound error if not.
    """
    client = resource_manager.Client()
    client.fetch_project(project_id)


def main():
    """
    Implements the entrypoint.
    """
    # configure logging
    logging.basicConfig(level=logging.INFO)

    # parse inputs
    project_id = os.environ['GCP_PROJECT_ID']  # required
    dataset_id = os.environ['BQ_DATASET']  # required
    slack_token = os.getenv('SLACK_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL')
    slack_results_url = os.getenv('SLACK_RESULTS_URL')
    fs_collection = os.getenv('FIRESTORE_COLLECTION')

    # validate inputs
    validate_project(project_id)

    # scan and load results into BigQuery
    title, version, rows = parse_profiles(*benchmark(project_id))
    table_id = load_bigquery(project_id, dataset_id, title, version, rows)

    # post to Slack, if specified
    if slack_token and slack_channel and slack_results_url:
        slack_notify(project_id, slack_token, slack_channel, slack_results_url)

    # Note: TODO please move this into a try-catch for all the above
    if fs_collection:
        firestore_report(fs_collection, table_id)


if __name__ == '__main__':
    main()
