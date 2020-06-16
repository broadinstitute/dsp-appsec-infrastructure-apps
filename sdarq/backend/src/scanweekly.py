from google.cloud import bigquery, pubsub_v1
import json
import os

sdarq_host = os.getenv('sdarq_host')
futures = dict()

def list_projects():
    client = bigquery.Client()
    sql_tables = """
            SELECT table_name FROM `cis.INFORMATION_SCHEMA.TABLES`
            """
    query_job_table = client.query(sql_tables)
    results_table = query_job_table.result()

    return results_table

def get_callback(f, data):
    def callback(f):
        try:
            print(f.result())
            futures.pop(data)
        except:  # noqa
            print("Please handle {} for {}.".format(f.exception(), data))

    return callback

def scan_projects(projects):
    topic_name = "cis-scans"
    project_id = "dsp-appsec-infra-prod"
    firestore_collection = "cis-scans"
    message = ""
    message = message.encode("utf-8")
    slack_channel = "#cis-scan-results"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    for row in projects:
        data = u"{}".format(row['table_name'])
        futures.update({data: None})
        # When a message is published, the client returns a future.
        future = publisher.publish(
                topic_path, 
                data=message,
                GCP_PROJECT_ID=row['table_name'],
                SLACK_CHANNEL=slack_channel,
                SLACK_RESULTS_URL=f"{sdarq_host}/cis/results?project_id={data}",
                FIRESTORE_COLLECTION=firestore_collection
        )
        futures[data] = future
        # Publish failures shall be handled in the callback function.
        future.add_done_callback(get_callback(future, data))


def main():
    scan_projects(list_projects())

if __name__ == '__main__':
    main() 