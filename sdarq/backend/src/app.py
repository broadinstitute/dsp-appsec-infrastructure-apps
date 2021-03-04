"""
This module
- sends a new service requirements request
        - creates a new product in Defect Dojo
        - optionally creates a Jira Ticket
        - notifies several Slack channels about service requirements request
- sends request to scan a GCP project against the CIS Benchmark
- get results from BigQuery for a scanned GCP project
- send a request for threat model
- scan a service via ZAP tool
"""
#!/usr/bin/env python3

import json
import logging
import os
import re
import threading
from typing import List
from urllib.parse import urlparse

import requests
from flask import Response, request
from flask_api import FlaskAPI
from flask_cors import cross_origin
from google.cloud import bigquery, firestore, pubsub_v1
from jira import JIRA
from trigger import parse_tags

import parse_data as parse_json_data
import slacknotify
from github_repo_dispatcher import github_repo_dispatcher

# Env variables
dojo_host = os.getenv('dojo_host')  # get Defect Dojo URL
dojo_user = os.getenv('dojo_user')
dojo_api_key = os.getenv('dojo_api_key')
slack_token = os.getenv('slack_token')
github_token = os.getenv('github_token', None)
github_org = os.getenv('github_org', None)
github_repo = os.getenv('github_repo', None)
github_event = os.getenv('github_event', "sdarq")
jira_username = os.getenv('jira_username')
jira_api_token = os.getenv('jira_api_token')
jira_instance = os.getenv('jira_instance')
sdarq_host = os.getenv('sdarq_host')
dojo_host_url = os.getenv('dojo_host_url')
firestore_collection = os.getenv('firestore_collection')
topic_name = os.environ['JOB_TOPIC']
pubsub_project_id = os.environ['PUBSUB_PROJECT_ID']
zap_topic_name = os.environ['ZAP_JOB_TOPIC']

# Create headers for DefectDojo API call
headers = {
    "content-type": "application/json",
    "Authorization": f"Token {dojo_api_key}",
}

app = FlaskAPI(__name__)

# Instantiate the Jira backend wrapper
global jira
jira = JIRA(basic_auth=(jira_username, jira_api_token),
            options={'server': jira_instance})

client = bigquery.Client()
db = firestore.Client()


@app.route('/health/', methods=['GET'])
def health():
    """
    Check health for ingress
    Args:
        None
    Returns:
        200 status
    """
    return ''


@app.route('/submit/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def submit():
    """
    Send new product to DefectDojo,
    create Jira ticket in teams board (optional),
    create Jira ticket in appsec team board for TM
    Args:
        formatted_jira_description
    Returns:
        200 status
    """
    json_data = request.get_json()
    dojo_name = json_data['Service']
    security_champion = json_data['Security champion']
    product_type = 1
    products_endpoint = f"{dojo_host_url}api/v2/products/"
    slack_channels_list = ['#dsp-security', '#appsec-internal']
    jira_project_key = "DSEC"

    # Create a Jira ticket for Threat Model in Appsec team board
    architecture_diagram = json_data['Architecture Diagram']
    github_url = json_data['Github URL']
    appsec_jira_ticket_description = github_url + '\n' + architecture_diagram
    appsec_jira_ticket_summury = 'Threat Model request ' + dojo_name

    jira_ticket_appsec = jira.create_issue(project=jira_project_key,
                                           summary=appsec_jira_ticket_summury,
                                           description=str(
                                               appsec_jira_ticket_description),
                                           issuetype={'name': 'Task'})
    logging.info("Jira ticket in appsec board created")

    # Create a Jira ticket if user chooses a Jira project
    if 'JiraProject' in json_data:
        project_key_id = json_data['JiraProject']
        jira_description = json.dumps(
            json_data['Ticket_Description']).strip('[]')

        formatted_jira_description = jira_description.strip(
            '", "').replace('", "', '\n-')

        jira_ticket = jira.create_issue(project=project_key_id,
                                        summary='New security requirements issue',
                                        description=str(
                                            formatted_jira_description),
                                        issuetype={'name': 'Task'})
        logging.info("Jira ticket in %s board created", project_key_id)

        # Delete Ticket_Description from json
        del json_data['Ticket_Description']

        # Create DefectDojo product
        data = {'name': dojo_name, 'description': parse_json_data.prepare_dojo_input(
            json_data), 'prod_type': product_type}
        res = requests.post(products_endpoint,
                            headers=headers, data=json.dumps(data))
        res.raise_for_status()
        product_id = res.json()['id']

        logging.info("Product created: %s", dojo_name)

        # Set Slack notification
        for channel in slack_channels_list:
            slacknotify.slacknotify_jira(channel, dojo_name, security_champion,
                                         product_id, dojo_host_url, jira_instance,
                                         project_key_id, jira_ticket)

    else:
        # Create DefectDojo product
        data = {'name': dojo_name, 'description': parse_json_data.prepare_dojo_input(
            json_data), 'prod_type': product_type}
        res = requests.post(products_endpoint,
                            headers=headers, data=json.dumps(data))
        res.raise_for_status()
        product_id = res.json()['id']

        logging.info("Product created: %s", dojo_name)

        # When Jira ticket creation is not selected
        for channel in slack_channels_list:
            slacknotify.slacknotify(
                channel, dojo_name, security_champion, product_id, dojo_host_url)

    if github_token and github_org and github_repo:
        github_repo_dispatcher(github_token, github_org,
                               github_repo, github_event, json_data)

    return ''


@app.route('/cis_results/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def cis_results():
    """
    Get CIS results for a specific google project
    Args:
        project_id: GCP project that will be scanned for security configurations
    Returns:
        json: Security scan results for given project_id
    """
    project_id_encoded = request.get_data()
    project_id = project_id_encoded.decode("utf-8")
    pattern = "^[a-z0-9][a-z0-9-_]{4,28}[a-z0-9]$"
    project_id_edited = project_id.strip('-').replace('-', '_')

    logging.info(
        "Request to read CIS scanner results for project %s ", project_id_edited)

    if re.match(pattern, project_id_edited):
        table_id = u"{0}.{1}.{2}".format(
            pubsub_project_id, 'cis', project_id_edited)
        try:
            client.get_table(table_id)
            sql_query = "SELECT table_id, FORMAT_TIMESTAMP('%m-%d-%G %T',TIMESTAMP_MILLIS(last_modified_time)) AS last_modified_date FROM `{0}.cis.__TABLES__` WHERE table_id=@tableid".format(
                str(pubsub_project_id))
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "tableid", "STRING", project_id_edited)
                ])
            query_job_table = client.query(sql_query, job_config=job_config)
            query_job_table.result()
            table_data = [dict(row) for row in query_job_table]
<<<<<<< HEAD
            sql_query_2 = "SELECT * FROM `{0}.cis.{1}` ORDER BY id".format(
                str(pubsub_project_id), str(project_id_edited))
=======
            sql_query_2 = "SELECT * FROM `{0}.cis.{1}` ORDER BY id".format(str(pubsub_project_id),
                                                                           str(project_id_edited))
>>>>>>> 08a8b95b84c8f57a34440009b63c59f5bd0255b6
            query_job = client.query(sql_query_2)
            query_job.result()
            findings = [dict(row) for row in query_job]
            table = json.dumps({'findings': findings, 'table': table_data},
                               indent=4, default=str)
            return table
        except Exception:
            status_code = 404
            notfound = f"""
            This Google project is not found! Did you make sure to supply the right GCP Project ID?
            You can verify the ID of the project you want to scan by running the following command:
            gcloud config list project --format='value(core.project)'
            """
            return Response(json.dumps({'statusText': notfound}), status=status_code, mimetype='application/json')


@app.route('/cis_scan/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def cis_scan():
    """
    Scans a specific google project
    """
    json_data = request.get_json()
    user_project_id = json_data['project_id']
    pattern = "^[a-z0-9][a-z0-9-_]{4,28}[a-z0-9]$"
    message = ""
    results_url = f"{sdarq_host}/cis/results?project_id={user_project_id}"
    message = message.encode("utf-8")

    if re.match(pattern, user_project_id):
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(pubsub_project_id, topic_name)
        user_proj = user_project_id.replace('-', '_')
        logging.info(
            "Request to assess security posture for project %s ", user_proj)
        db.collection(firestore_collection).document(user_proj)
        if 'slack_channel' in json_data:
            slack_channel = f"#{json_data['slack_channel']}"
            publisher.publish(topic_path,
                              data=message,
                              GCP_PROJECT_ID=user_project_id,
                              SLACK_CHANNEL=slack_channel,
                              SLACK_RESULTS_URL=results_url,
                              FIRESTORE_COLLECTION=firestore_collection)
        else:
            publisher.publish(topic_path,
                              data=message,
                              GCP_PROJECT_ID=user_project_id,
                              FIRESTORE_COLLECTION=firestore_collection)

    callback_done = threading.Event()

    def on_snapshot(doc_snapshots: List[firestore.DocumentSnapshot], _changes, _read_time):
        for doc in doc_snapshots:
            if doc.exists:
                callback_done.set()
                return

    user_proj = user_project_id.replace('-', '_')
    doc_ref = db.collection(firestore_collection).document(user_proj)
    doc_ref.delete()
    doc_watch = doc_ref.on_snapshot(on_snapshot)
    callback_done.wait(timeout=3600)
    doc_watch.unsubscribe()
    doc = doc_ref.get()

    check_dict = doc.to_dict()
    if check_dict:
        status_code = 404
        text_message = check_dict['Error']
        doc_ref.delete()
        return Response(json.dumps({'statusText': text_message}), status=status_code, mimetype='application/json')
    else:
        doc_ref.delete()
        return ''


@app.route('/request_tm/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def request_tm():
    """
    Creates a request for threat model for a specific service
    Creates a Jira ticket and notifies team in Slack
    Args:
        JSON data supplied by user
    """
    user_data = request.get_json()
    security_champion = user_data['Eng']
    request_type = user_data['Type']
    project_name = user_data['Name']
    slack_channels_list = ['#dsp-security', '#appsec-internal']
    jira_project_key = "DSEC"

    appsec_jira_ticket_summury = user_data['Type'] + user_data['Name']
    appsec_jira_ticket_description = user_data['Diagram'] + '\n' + \
        user_data['Document'] + '\n' + user_data['Github']

    logging.info("Request for threat model for project %s ", project_name)

    jira_ticket_appsec = jira.create_issue(project=jira_project_key,
                                           summary=appsec_jira_ticket_summury,
                                           description=str(
                                               appsec_jira_ticket_description),
                                           issuetype={'name': 'Task'})
    logging.info(
        "Jira ticket in appsec board for project %s threat model", project_name)

    for channel in slack_channels_list:
        slacknotify.slacknotify_threat_model(channel, security_champion,
                                             request_type, project_name, jira_instance, jira_ticket_appsec, jira_project_key)

    return ''


@app.route('/zap_scan/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def zap_scan():
    """
    Scan a service via ZAP tool
    Args:
        Json file
    Returns:
        200 if a Zap Scan is triggered
        404 if project not found
    """
    json_data = request.get_json()
    message = b""
    user_supplied_url = json_data['URL']
    dev_slack_channel = f"#{json_data['slack_channel']}"
    endpoint = f"{dojo_host_url}api/v2/endpoints/"

    publisher = pubsub_v1.PublisherClient()
    zap_topic_path = publisher.topic_path(pubsub_project_id, zap_topic_name)

    res = requests.get(endpoint, headers=headers, timeout=30)
    res.raise_for_status()
    endpoints = res.json()["results"]

    if not re.match(r'^(http|https)://', user_supplied_url):
        user_supplied_url = 'https://' + user_supplied_url

    parsed_user_url = urlparse(user_supplied_url)
    for endpoint in endpoints:
        if endpoint['host'] == parsed_user_url.netloc:
            service_codex_project, default_slack_channel, service_scan_type = parse_tags(
                endpoint)
            if endpoint['path'] == None:
                service_full_endpoint = f"{endpoint['protocol']}://{endpoint['host']}"
            else:
                service_full_endpoint = f"{endpoint['protocol']}://{endpoint['host']}{endpoint['path']}"
            severities = parse_json_data.parse_severities(
                json_data['severities'])
            publisher.publish(zap_topic_path,
                              data=message,
                              URL=service_full_endpoint,
                              CODEDX_PROJECT=service_codex_project,
                              SCAN_TYPE=service_scan_type.name,
                              SEVERITIES=severities,
                              SLACK_CHANNEL=dev_slack_channel)

            return ''
    else:
        status_code = 404
        text_message = f"""
        You should NOT run a security pentest against the URL you entered, or maybe it doesn't exist in AppSec list.
        """
        return Response(json.dumps({'statusText': text_message}), status=status_code, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', 8080)))
