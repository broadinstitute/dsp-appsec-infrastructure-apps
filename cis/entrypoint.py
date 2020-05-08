#!/usr/bin/env python3

import json
import os
import subprocess
import slack
from google.cloud import resource_manager
from google.cloud import bigquery
from google.cloud import firestore


GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BQ_DATASET = os.getenv('BQ_DATASET')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
RESULTS_URL = os.getenv('RESULTS_URL')
FIRESTORE_COLLECTION = os.getenv('FIRESTORE_COLLECTION')
BENCHMARK_PROFILE = 'inspec-gcp-cis-benchmark'


def benchmark():
    args = f'''
        inspec exec {BENCHMARK_PROFILE} -t gcp:// --reporter json
            --input gcp_project_id={GCP_PROJECT_ID}
    '''.split()
    proc = subprocess.run(args, capture_output=True, text=True)

    # normal exit codes as documented at
    # https://www.inspec.io/docs/reference/cli
    if proc.returncode not in (0, 100, 101):
        print(proc.stderr)
        raise subprocess.CalledProcessError(proc.returncode, proc.args)

    return json.loads(proc.stdout)['profiles']


def parse_profiles(profiles):
    profile = None
    for p in profiles:
        if p['name'] == 'inspec-gcp':
            version = p['version']
        elif p['name'] == BENCHMARK_PROFILE:
            profile = p

    title = profile['title']
    rows = []
    for c in profile['controls']:
        failures = []
        for r in c['results']:
            if r['status'] != 'failed' or 'exception' in r:
                continue
            failures.append(
                r['code_desc']
                .replace(f'[{GCP_PROJECT_ID}] ', '', 1)
                .replace('cmp == nil', 'be empty')
                .replace('cmp ==', 'equal')
            )
        if not failures:
            continue

        for d in c['descriptions']:
            if d['label'] != 'rationale':
                continue
            rationale = d['data']

        tags = c['tags']
        refs = [ref['url'] for ref in c['refs']]

        rows.append({
            'id': tags['cis_gcp'],
            'level': tags['cis_level'],
            'title': c['title'],
            'failures': failures,
            'description': c['desc'],
            'rationale': rationale,
            'refs': refs,
        })

    return title, version, rows


def load_bigquery(table_desc, version, rows):
    if not rows:
        return

    bquery = bigquery.Client()
    table_id = GCP_PROJECT_ID.replace('-', '_')
    table = bquery.dataset(BQ_DATASET).table(table_id)

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
        destination_table_description=table_desc,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
        ),
        labels={
            'gcp-project': GCP_PROJECT_ID,
            'inspec-version': version.replace('.', '_'),
        },
    )

    job = bquery.load_table_from_json(rows, table, job_config=job_config)
    job.result()  # wait for completion
    print(f"Loaded {job.output_rows} rows into {BQ_DATASET}.{table_id}")
    firestore_report(table_id, FIRESTORE_COLLECTION)


def firestore_report(table_id, FIRESTORE_COLLECTION):
    db_firestore = firestore.Client()
    doc_ref = db_firestore.collection(FIRESTORE_COLLECTION).document(table_id)
    doc_ref.set({})


def slack_notify(GCP_PROJECT_ID, SLACK_CHANNEL, RESULTS_URL):
    client = slack.WebClient(SLACK_TOKEN)
    response = client.chat_postMessage(
        channel=SLACK_CHANNEL,
        attachments=[{"blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Check `{0}` results* :blue_book:" .format(str(GCP_PROJECT_ID))
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
                        "url": "{0}/cis/results?project_id={1}" .format(str(RESULTS_URL), str(GCP_PROJECT_ID))
                    }
                ]
            }], "color": "#0a88ab"}]
    )


def project_exists(GCP_PROJECT_ID: str) -> bool:
    """
    Function that checks if a project exists in GCP
    Args:
        project_id: GCP Project ID
    Returns:
        True if the project exists, false otherwise
    """
    result = False
    all_projects = []
    for project in resource_manager.Client().list_projects():
        all_projects.append(project.name)
    if GCP_PROJECT_ID in all_projects:
        result = True
    else:
        result = False
    return result


def main():
    # Only load to bigquery if gcp project exists
    if project_exists(GCP_PROJECT_ID):
        load_bigquery(*parse_profiles(benchmark()))

        # Check env variable set and not empty
        if os.environ.get('SLACK_CHANNEL') is not None and SLACK_CHANNEL:
            slack_notify(GCP_PROJECT_ID, SLACK_CHANNEL, RESULTS_URL)


if __name__ == '__main__':
    main()
