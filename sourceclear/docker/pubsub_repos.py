from google.cloud import bigquery
from google.cloud import resource_manager
from google.cloud import pubsub_v1
import os

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
JOB_TOPIC = os.getenv('JOB_TOPIC')

futures = dict()

def get_repos():
    bquery = bigquery.Client()

    query_job = bquery.query((f"SELECT * FROM {GCP_PROJECT_ID}.dsp_appsec_scans.sourceclear_repos"))

    return query_job.result()

def get_callback(f, data):
    def callback(f):
        try:
            print(f.result())
            futures.pop(data)
        except:
            print("Please handle {} for {}.".format(f.exception(), data))

    return callback

def pub_repos(repos):

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT_ID, JOB_TOPIC)

    for row in repos:
        container_name = u"{}-{}{}".format(row['org'],row['project'],row['subdir'].replace("/", "-"))
        futures.update({container_name: None})
        future = publisher.publish(
            topic_path, 
            data=container_name.encode("utf-8"),
            CONTAINER_NAME=container_name,
            PROJECT=row['project'],
            BRANCH=row['branch'],
            REPO=str(row['org'], "/", row['project']),
            ORG=row['org'],
            SUBDIR=row['subdir']
        )
        futures[container_name] = future
        
        future.add_done_callback(get_callback(future, container_name))

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
    if project_exists(GCP_PROJECT_ID):
        pub_repos(get_repos())


if __name__ == '__main__':
    main()