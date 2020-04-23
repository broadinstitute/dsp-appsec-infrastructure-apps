#!/usr/bin/env python3

from google.cloud import bigquery
import json
import os
import subprocess

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BQ_DATASET = os.getenv('BQ_DATASET')
slack_token = os.getenv('slack_token')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
RESULTS_URL = os.getenv('RESULTS_URL')

BENCHMARK_PROFILE = 'inspec-gcp-cis-benchmark'


def benchmark():
    args = f'''
        inspec exec {BENCHMARK_PROFILE} -t gcp:// --reporter json
            --input gcp_project_id={GCP_PROJECT_ID}
    '''.split()
    p = subprocess.run(args, capture_output=True, text=True)

    # normal exit codes as documented at
    # https://www.inspec.io/docs/reference/cli
    if p.returncode not in (0, 100, 101):
        print(p.stderr)
        raise subprocess.CalledProcessError(p.returncode, p.args)

    return json.loads(p.stdout)['profiles']


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

    bq = bigquery.Client()
    table_id = GCP_PROJECT_ID.replace('-', '_')
    table = bq.dataset(BQ_DATASET).table(table_id)

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

    job = bq.load_table_from_json(rows, table, job_config=job_config)
    job.result()  # wait for completion
    print(f"Loaded {job.output_rows} rows into {BQ_DATASET}.{table_id}")


def slack_notify(GCP_PROJECT_ID, SLACK_CHANNEL, RESULTS_URL){
    client = slack.WebClient(slack_token)
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
                        "url": "{0}/cis/results?project_id={1}" .format(str(RESULTS_URL),str(GCP_PROJECT_ID))
                    }
                ]
            }
        ],
        "color": "#0a88ab"
    } ])
    return ''
}

def main():
    load_bigquery(*parse_profiles(benchmark()))
    if SLACK_CHANNEL != "":
        slack_notify(GCP_PROJECT_ID, SLACK_CHANNEL, RESULTS_URL)          

if __name__ == '__main__':
    main()

