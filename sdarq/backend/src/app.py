#!/usr/bin/env python3

from flask import request, make_response, Response
from flask_api import FlaskAPI
from flask_cors import CORS, cross_origin
from google.cloud import bigquery
from google.cloud import pubsub_v1
from jira import JIRA
import slacknotify as slacknotify
import defectdojo as wrapper
import os
import re
import slack
import datetime
import json
from google.cloud import firestore

# Env variables
dojo_host = os.getenv('dojo_host')
dojo_user = os.getenv('dojo_user')
dojo_api_key = os.getenv('dojo_api_key')
slack_token = os.getenv('slack_token')
jira_username = os.getenv('jira_username')
jira_api_token = os.getenv('jira_api_token')
jira_instance = os.getenv('jira_instance')
sdarq_host = os.getenv('sdarq_host')
dojo_host_url = os.getenv('dojo_host_url')

# Instantiate the DefectDojo backend wrapper
dd = wrapper.DefectDojoAPI(dojo_host, dojo_api_key, dojo_user, debug=True)
app = FlaskAPI(__name__)

# Instantiate the Jira backend wrapper
global jira
jira = JIRA(basic_auth=(jira_username, jira_api_token), options={'server': jira_instance })


@app.route('/health/', methods=['GET'])
def health():
    """
    Check health for ingress
    Args:
        nformatted_jira_description
    Returns:
        200 status
    """
    return ''


@app.route('/submit/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def submit():
    """
    Send new product to DefectDojo
    Args:
        nformatted_jira_description
    Returns:
        200 status
    """
    json_data = request.get_json()
    dojo_name = json_data['Service']
    security_champion = json_data['Security champion']

    # Create a product in DefectDojo
    product_type = 1
    product = dd.create_product(
        dojo_name, "Initial Engagement Placeholder", product_type)

    if product.success:
        product_id = product.id()
    else:
        raise Exception("dd.create_product(): " + str(product))

    def prepare_dojo_input(json_data):
        """ Prepares defect dojo description input """
        data = json.dumps(json_data).strip('{}')
        data1 = data.strip(',').replace(',', ' \n')
        data2 = data1.strip('[').replace('[', ' ')
        data3 = data2.strip(']').replace(']', ' ')
        data4 = data3.strip('""').replace('"', ' ')

        return data4

    # Create a Jira ticket if user chooses a Jira project
    slack_channels_list = ['#new-sec-service-req', '#zap-test']

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

        # Delete Ticket_Description from json, so it will not be added to DefectDojo product description
        del json_data['Ticket_Description']

        # Set product description
        product_description = dd.set_product(
            product_id, description=prepare_dojo_input(json_data))

        # Set Slack notification
        for channel in slack_channels_list:
            if channel == '#zap-test':
                slacknotify.slacknotify_jira_qa(
                    slack_token, channel, dojo_name, security_champion, product_id, dojo_host_url, jira_instance, project_key_id, jira_ticket)
            else:
                slacknotify.slacknotify_jira(slack_token, channel, dojo_name, security_champion,
                                             product_id, dojo_host_url, jira_instance, project_key_id, jira_ticket)

    else:
        # When Jira ticket creation is not selected
        for channel in slack_channels_list:
            if channel == '#zap-test':
                slacknotify.slacknotify_qa(
                    slack_token, channel, dojo_name, security_champion, product_id, dojo_host_url)
            else:
                slacknotify.slacknotify(
                    slack_token, channel, dojo_name, security_champion, product_id, dojo_host_url)

         # Set product description
        product_description = dd.set_product(
            product_id, description=prepare_dojo_input(json_data))


@app.route('/cis_results/<project_id>', methods=['GET'])
@cross_origin(origins=sdarq_host)
def cis_results(project_id):
    """
    Get CIS results for a specific google project
    Args:
        project_id: GCP project that will be scanned for security configurations
    Returns:
        json: Security scan results for given project_id
    """
    project_id = project_id
    pattern = "^[a-z][a-z0-9-_]{4,28}[a-z0-9]$"
    project_id_edited = project_id.strip('-').replace('-', '_')

    if re.match(pattern, project_id_edited):
        client = bigquery.Client()
        sql_tables = """
                SELECT table_name FROM `cis.INFORMATION_SCHEMA.TABLES` WHERE table_name=@corpus
                """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "corpus", "STRING", project_id_edited)
            ])
        query_job_table = client.query(sql_tables, job_config=job_config)
        results_table = query_job_table.result()
        tables = [dict(row) for row in query_job_table]
        json_obj_tables = json.dumps(tables)
        if results_table.total_rows != 0:
            sql = "SELECT * FROM `dsp-appsec-infra-prod.cis.{0}` WHERE id!='5.3'".format(
                str(project_id_edited))
            query_job = client.query(sql)
            results = query_job.result()
            records = [dict(row) for row in query_job]
            json_obj = json.dumps(records)
            return json_obj
        else:
            notfound = f"""
            This Google project is not found! Did you make sure to supply the right GCP Project ID? 
            You can verify the ID of the project you want to scan by running the following command: 
            gcloud config list project --format='value(core.project)'
            """
            return Response(json.dumps({'statusText': notfound}), status=404, mimetype='application/json')


@app.route('/cis_scan/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def cis_scan():
    """
    Scans a specific google project
    """
    json_data = request.get_json()
    user_project_id = json_data['project_id']
    pattern = "^[a-z][a-z0-9-_]{4,28}[a-z0-9]$"
    results_url = sdarq_host
    topic_name = "cis-scans"
    project_id = "dsp-appsec-infra-prod"
    message = ""
    message = message.encode("utf-8")
    firestore_collection = 'cis_scans'
    all_projects = []

    if re.match(pattern, user_project_id):
                publisher = pubsub_v1.PublisherClient()
                topic_path = publisher.topic_path(project_id, topic_name)
                if 'slack_channel' in json_data:
                    slack_channel = json_data['slack_channel']
                    publisher.publish(topic_path,
                                    data=message,
                                    GCP_PROJECT_ID=user_project_id,
                                    SLACK_CHANNEL=slack_channel,
                                    RESULTS_URL=results_url,
                                    FIRESTORE_COLLECTION=firestore_collection)
                else:
                    publisher.publish(topic_path,
                                    data=message,
                                    GCP_PROJECT_ID=user_project_id,
                                    FIRESTORE_COLLECTION=firestore_collection)

                # Check if a document exists in Firestore
                check = False
                while check is False:
                    db = firestore.Client()
                    doc_ref = db.collection(
                        firestore_collection).document(user_project_id)
                    doc = doc_ref.get()
                    if doc.exists:
                        check = True
                    else:
                        check = False

                db.collection(firestore_collection).document(
                    user_project_id).delete()

                return Response(json.dumps({'statusText': 'Doc found!', 'status': 'true'}), status=200, mimetype='application/json')
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
    