"""
This module
- sends a new service requirements request
        - creates a new product in Defect Dojo
        - optionally creates a Jira Ticket
        - notifies several Slack channels about service requirements request
        - creates a new security controls template for a new service/product
- sends request to scan a GCP project against the CIS Benchmark
- get results from BigQuery for a scanned GCP project
- send a request for threat model
- send a request for security pentest
- scan a service via ZAP tool
- add security controls for a service
- edit security controls for a service
- list all security controls for all services
- calculates the risk of a Jira ticket and notifies AppSec team
"""
#!/usr/bin/env python3

import imp
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
from jsonschema import validate
from trigger import parse_tags

import parse_data as parse_json_data
import slacknotify
from schemas.cis_scan_schema import cis_scan_schema
from schemas.edit_security_controls_schema import edit_security_controls_schema
from schemas.manual_pentest_request_schema import mp_schema
from schemas.new_service_schema import new_service_schema
from schemas.security_controls_schema import security_controls_schema
from schemas.threat_model_request_schema import tm_schema
from schemas.zap_scan_schema import zap_scan_schema

dojo_host = os.getenv('dojo_host')
dojo_api_key = os.getenv('dojo_api_key')
slack_token = os.getenv('slack_token')
jira_username = os.getenv('jira_username')
jira_api_token = os.getenv('jira_api_token')
jira_instance = os.getenv('jira_instance')
sdarq_host = os.getenv('sdarq_host')
dojo_host_url = os.getenv('dojo_host_url')
appsec_slack_channel = os.getenv('appsec_slack_channel')
appsec_jira_project_key = os.getenv('appsec_jira_project_key')
jtra_slack_channel = os.getenv('jtra_slack_channel')

firestore_collection = os.environ['CIS_FIRESTORE_COLLECTION']
cis_topic_name = os.environ['CIS_JOB_TOPIC']
pubsub_project_id = os.environ['PUBSUB_PROJECT_ID']
zap_topic_name = os.environ['ZAP_JOB_TOPIC']
security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']


headers = {
    "content-type": "application/json",
    "Authorization": f"Token {dojo_api_key}",
}
logging.basicConfig(level=logging.INFO)

app = FlaskAPI(__name__)

global jira
jira = JIRA(basic_auth=(jira_username, jira_api_token),
            options={'server': jira_instance})

client = bigquery.Client()

db = firestore.Client()


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'deny'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = 'default-src \'self\''
    return response


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
    Create new product to DefectDojo,
    create Jira ticket in teams board (optional),
    create Jira ticket in appsec team board for TM
    Args:
        Json data
    Returns:
        200 status
    """
    json_data = request.get_json()
    dojo_name = json_data['Service']
    security_champion = json_data['Security champion']
    product_type = 1
    products_endpoint = f"{dojo_host}api/v2/products/"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    architecture_diagram = json_data['Architecture Diagram']
    github_url = json_data['Github URL']
    appsec_jira_ticket_description = github_url + '\n' + architecture_diagram
    appsec_jira_ticket_summury = 'Threat Model request ' + dojo_name

    try:
        validate(instance=json_data, schema=new_service_schema)
        if 'JiraProject' in json_data:
            project_key_id = json_data['JiraProject']
            dev_jira_ticket_summury = dojo_name + ' security requirements'
            jira_description = json.dumps(
                json_data['Ticket_Description']).strip('[]')

            formatted_jira_description = jira_description.strip(
                '", "').replace('", "', '\n-')

            jira_ticket = jira.create_issue(project=project_key_id,
                                            summary=dev_jira_ticket_summury,
                                            description=str(
                                                formatted_jira_description),
                                            issuetype={'name': 'Task'})
            logging.info("Jira ticket in %s board created by %s",
                         project_key_id, user_email)

            del json_data['Ticket_Description']

            data = {'name': dojo_name, 'description': parse_json_data.prepare_dojo_input(
                json_data), 'prod_type': product_type}
            res = requests.post(products_endpoint,
                                headers=headers, data=json.dumps(data))
            res.raise_for_status()
            product_id = res.json()['id']

            logging.info("Product created: %s by %s request",
                         dojo_name, user_email)

            slacknotify.slacknotify_jira(appsec_slack_channel, dojo_name, security_champion,
                                         product_id, dojo_host_url, jira_instance,
                                         project_key_id, jira_ticket)
        else:
            data = {'name': dojo_name, 'description': parse_json_data.prepare_dojo_input(
                json_data), 'prod_type': product_type}
            res = requests.post(products_endpoint,
                                headers=headers, data=json.dumps(data))
            res.raise_for_status()
            product_id = res.json()['id']

            logging.info("Product created: %s by %s request",
                         dojo_name, user_email)

            slacknotify.slacknotify(
                appsec_slack_channel, dojo_name, security_champion, product_id, dojo_host_url)

        jira.create_issue(project=appsec_jira_project_key,
                          summary=appsec_jira_ticket_summury,
                          description=str(
                              appsec_jira_ticket_description),
                          issuetype={'name': 'Task'})
        logging.info("Jira ticket in appsec board created")

        return ''
    except Exception as error:
        error_message = f"Exception /submit enspoint: {error}"
        logging.warning(error_message)
        status_code = 404
        message = """
        There is something wrong with the input! Server did not respond correctly to your request! 
        """
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


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
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    logging.info(
        "Request by %s to read CIS scanner results for project %s ", user_email, project_id_edited)

    if re.match(pattern, project_id_edited):
        table_id = u"{0}.{1}.{2}".format(
            pubsub_project_id, 'cis', project_id_edited)
        try:
            last_modified_datetime = client.get_table(
                table_id).modified.strftime('%G-%m-%dT%H:%M:%SZ')
            sql_query = f'''
                SELECT
                    benchmark, id, level,
                    CAST(CAST(impact AS FLOAT64) * 10 AS INT64) AS cvss,
                    title, failures, description, rationale, refs,
                FROM `{table_id}`
                WHERE DATE(_PARTITIONTIME) = DATE(@last_modified_datetime)
                AND ARRAY_LENGTH(failures) > 0
                AND timestamp IN (
                    SELECT MAX(timestamp) FROM `{table_id}`
                )
                ORDER BY level, cvss DESC, id
            '''
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "last_modified_datetime", "STRING", last_modified_datetime)
                ]
            )
            query_job = client.query(sql_query, job_config=job_config)
            query_job.result()
            findings = [dict(row) for row in query_job]
            return json.dumps({
                'findings': findings,
                'meta': {
                    'projectId': project_id,
                    'lastModifiedDatetime': last_modified_datetime,
                }
            }, indent=2)
        except Exception as error:
            error_message = f"Exception /cis_results enspoint: {error}"
            logging.warning(error_message)
            status_code = 404
            notfound = """
            This Google project is not found! Did you make sure to supply the right GCP Project ID? Please check again!
            """
            return Response(json.dumps({'statusText': notfound}), status=status_code, mimetype='application/json')
    else:
        status_code = 404
        message = """
        Your GCP project_id is not valid! Enter a valid value!
        """
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


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
    results_url = f"{sdarq_host}/gcp-project-security-posture/results?project_id={user_project_id}"
    message = message.encode("utf-8")
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if re.match(pattern, user_project_id):
        try:
            validate(instance=json_data, schema=cis_scan_schema)
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(
                pubsub_project_id, cis_topic_name)
            user_proj = user_project_id.replace('-', '_')
            logging.info(
                "Request by %s to assess security posture for project %s ", user_email, user_proj)
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
            callback_done.wait(timeout=36000)
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
        except Exception as error:
            error_message = f"Exception /cis_scan enspoint: {error}"
            logging.warning(error_message)
            status_code = 404
            return Response(json.dumps({'statusText': error}), status=status_code, mimetype='application/json')
    else:
        message = """
        Your GCP project_id is not valid! Enter a valid value!
        """
        status_code = 404
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


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
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    try:
        validate(instance=user_data, schema=tm_schema)
        security_champion = user_data['Eng']
        request_type = user_data['Type']
        project_name = user_data['Name']
        logging.info("Threat model request for %s by %s",
                     project_name, user_email)
        appsec_jira_ticket_summury = user_data['Type'] + user_data['Name']
        appsec_jira_ticket_description = user_data['Diagram'] + \
            '\n' + user_data['Document'] + \
            '\n' + user_data['Github']

        jira_ticket_appsec = jira.create_issue(project=appsec_jira_project_key,
                                               summary=appsec_jira_ticket_summury,
                                               description=str(
                                                   appsec_jira_ticket_description),
                                               issuetype={'name': 'Task'})
        logging.info(
            "Jira ticket created in appsec board for %s threat model", project_name)

        slacknotify.slacknotify_threat_model(appsec_slack_channel,
                                             security_champion,
                                             request_type, project_name,
                                             jira_instance,
                                             jira_ticket_appsec,
                                             appsec_jira_project_key)
        return ''
    except Exception as error:
        error_message = f"Exception /request_tm enspoint: {error}"
        logging.warning(error_message)
        status_code = 404
        message = """
        There is something wrong with the input! Server did not respond correctly to your request! 
        """
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


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
    endpoint = f"{dojo_host}api/v2/endpoints?tag=scan&limit=1000"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    status_code = 404
    text_message = """
                    You should NOT run a security pentest against the URL you entered, 
                    or maybe it doesn't exist in AppSec list. Please contact AppSec team.
                    """
    try:
        validate(instance=json_data, schema=zap_scan_schema)
        user_supplied_url = json_data['URL']
        dev_slack_channel = f"#{json_data['slack_channel']}"
        publisher = pubsub_v1.PublisherClient()
        zap_topic_path = publisher.topic_path(
            pubsub_project_id, zap_topic_name)

        res = requests.get(endpoint, headers=headers, timeout=30)
        res.raise_for_status()
        endpoints = res.json()["results"]

        if not re.match(r'^(http|https)://', user_supplied_url):
            user_supplied_url = 'https://' + user_supplied_url

        parsed_user_url = urlparse(user_supplied_url)
        for endpoint in endpoints:
            if endpoint['host'] == parsed_user_url.netloc:
                service_codex_project, default_slack_channel, service_scan_type, engagement_id = parse_tags(
                    endpoint)
                if endpoint['path'] is None:
                    service_full_endpoint = f"{endpoint['protocol']}://{endpoint['host']}"
                else:
                    if endpoint['path'].strip('/') == parsed_user_url.path.strip('/'):
                        service_full_endpoint = f"{endpoint['protocol']}://{endpoint['host']}/{endpoint['path']}"
                    else:
                        logging.info(
                            "User %s requested to scan via ZAP a service that does not exist in DefectDojo endpoint list", user_email)
                        return Response(json.dumps({'statusText': text_message}), status=status_code, mimetype='application/json')
                severities = parse_json_data.parse_severities(
                    json_data['severities'])
                publisher.publish(zap_topic_path,
                                  data=message,
                                  URL=service_full_endpoint,
                                  CODEDX_PROJECT=service_codex_project,
                                  SCAN_TYPE=service_scan_type.name,
                                  SEVERITIES=severities,
                                  SLACK_CHANNEL=dev_slack_channel,
                                  ENGAGEMENT_ID=engagement_id)
                logging.info("User %s requested to scan via ZAP %s service",
                             user_email, service_full_endpoint)
                return ''
        else:
            logging.info(
                "User %s requested to scan via ZAP a service that does not exist in DefectDojo endpoint list", user_email)
            return Response(json.dumps({'statusText': text_message}), status=status_code, mimetype='application/json')
    except Exception as error:
        error_message = f"Exception /zap_scan enspoint: {error}"
        logging.warning(error_message)
        message = """ 
        There is something wrong with the input! Server did not respond correctly to your request! 
        """
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


@app.route('/create_sec_control_template/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def create_sec_control_template():
    """
    Store data to Firestore
    Args: Provided json data from user
    Returns: 200 if data stored to Firestore
             404 if input is invalid/ service already exists
    """
    json_data = request.get_json()
    service_name = json_data['service']
    pattern = "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if re.match(pattern, service_name):
        try:
            validate(instance=json_data, schema=security_controls_schema)
            doc_ref = db.collection(security_controls_firestore_collection).document(
                service_name.lower())
            doc = doc_ref.get()
            if bool(doc.to_dict()) is True:
                message = """
                This service already exists, if you want to edit it, go to the edit page.
                """
                logging.info(
                    "User %s requested to create SCT for a service, but it already exists", user_email)
                return Response(json.dumps({'statusText': message}), status=404, mimetype='application/json')
            else:
                db.collection(security_controls_firestore_collection).document(
                    service_name.lower()).set(json_data)
                logging.info(
                    "A new security controls template is created by %s", user_email)
                return ''
        except Exception as error:
            error_message = f"Exception /create_sec_controls_template enspoint: {error}"
            logging.warning(error_message)
            status_code = 404
            message = """ 
            There is something wrong with the input! Server did not respond correctly to your request! 
            """
            return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')
    else:
        message = """
        Invalid input! Please make sure you include numbers, -, _ and alphabetical characters.
        """
        logging.info(
            "User %s requested to create SCT for a service, but INVALID input was provided", user_email)
        return Response(json.dumps({'statusText': message}), status=404, mimetype='application/json')


@app.route('/edit_sec_controls/', methods=['PUT'])
@cross_origin(origins=sdarq_host)
def edit_sec_controls():
    """
    Edit data for a specific service
    Args: Provided json data from user
    Returns: 200 if data stored to Firestore
             404 if input is invalid/service does not exist
    """
    json_data = request.get_json()
    service_name = json_data['service']
    pattern = "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if re.match(pattern, service_name):
        try:
            validate(instance=json_data, schema=edit_security_controls_schema)
            doc_ref = db.collection(security_controls_firestore_collection).document(
                service_name.lower())
            doc = doc_ref.get()
            if bool(doc.to_dict()) is True:
                db.collection(security_controls_firestore_collection).document(
                    service_name.lower()).set(json_data)
                logging.info(
                    "Security controls for the choosen service have changed by %s !", user_email)
                return ''
            else:
                message = """
                This service does not exist!
                """
                logging.info(
                    "User %s requested to edit a service security controls, but this service does not exist!", user_email)
                return Response(json.dumps({'statusText': message}), status=404, mimetype='application/json')
        except Exception as error:
            error_message = f"Exception /edit_sec_controls enspoint: {error}"
            logging.warning(error_message)
            message = """ 
            There is something wrong with the input! Server did not respond correctly to your request! 
            """
            status_code = 404
            return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')
    else:
        message = """
        Invalid input! Please make sure you include numbers, -, _ and alphabetical characters.
        """
        logging.info(
            "User %s requested to edit SCT for a service, but INVALID input was provided", user_email)
        return Response(json.dumps({'statusText': message}), status=404, mimetype='application/json')


@app.route('/get_sec_controls/', methods=['GET'])
@cross_origin(origins=sdarq_host)
def get_sec_controls():
    """
    Get all data from Firestore
    Args: None
    Returns: Json data
    """
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    data = []
    try:
        docs = db.collection(security_controls_firestore_collection).stream()
        logging.info(
            "User %s read security controls for the list of services.", user_email)
        for doc in docs:
            data.append(doc.to_dict())
        return data
    except Exception as error:
        error_message = f"Exception /get_sec_controls enspoint: {error}"
        logging.warning(error_message)
        message = """
        Server can't get security controls! Contact AppSec team for more information.
        """
        status_code = 404
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


@app.route('/get_sec_controls_service/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def get_sec_controls_service():
    """
    Get all security controls for a service
    Args: Service name (Json format)
    Returns: Json data if 200
             404 if project not found
    """
    json_data = request.get_json()
    service_name = json_data['service']
    pattern = "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if re.match(pattern, service_name, re.IGNORECASE):
        try:
            doc_ref = db.collection(security_controls_firestore_collection).document(
                service_name.lower())
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                message = """
                This service does not exist!
                """
                logging.info(
                    "User %s requested to read security controls of a service that does not exist.", user_email)
                return Response(json.dumps({'statusText': message}), status=404, mimetype='application/json')
        except Exception as error:
            error_message = f"Exception /get_sec_controls_service enspoint: {error}"
            logging.warning(error_message)
            message = """ 
            There is something wrong with the input! Server did not respond correctly to your request! 
            """
            status_code = 404
            return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')
    else:
        message = """
        Please enter a valid value for your service name! Contact AppSec team for more information.
        """
        logging.info(
            "User %s did not provide a valid value for the service name to read security controls.", user_email)
        return Response(json.dumps({'statusText': message}), status=404, mimetype='application/json')


@app.route('/request_manual_pentest/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def request_manual_pentest():
    """
    Creates a request for security pentest for a specific service
    Creates a Jira ticket and notifies team in Slack
    Args:
        JSON data supplied by user
    """
    user_data = request.get_json()
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    try:
        validate(instance=user_data, schema=mp_schema)
        security_champion = user_data['security_champion']
        project_name = user_data['service']

        appsec_jira_ticket_summury = 'Security pentest request for ' + \
            user_data['service']
        appsec_jira_ticket_description = 'URL to pentest: ' + user_data['URL'] + \
            '\n' + 'Environment: ' + user_data['env'] + \
            '\n' + 'Permission levels:' + user_data['permission_level'] + \
            '\n' + 'Documentation: ' + user_data['document'] + \
            '\n' + 'Security champion: ' + user_data['security_champion']
        jira_ticket_appsec = jira.create_issue(project=appsec_jira_project_key,
                                               summary=appsec_jira_ticket_summury,
                                               description=str(
                                                   appsec_jira_ticket_description),
                                               issuetype={'name': 'Task'})
        logging.info(
            "Jira ticket created in appsec board for %s security pentest request by %s", project_name, user_email)

        slacknotify.slacknotify_security_pentest(appsec_slack_channel,
                                                 security_champion,
                                                 project_name,
                                                 jira_instance,
                                                 jira_ticket_appsec,
                                                 appsec_jira_project_key)
        return ''
    except Exception as error:
        error_message = f"Exception /request_manual_pentest enspoint: {error}"
        logging.warning(error_message)
        status_code = 404
        message = """
        There is something wrong with the input! Server did not respond correctly to your request! 
        """
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


@app.route('/submitJTRA/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def submitJTRA():
    """
    Calculates the risk based on the user data and notifies AppSec team for the review
    Args:
        JSON data supplied by user
    """
    user_data = request.get_json()
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    try:
        if user_data['high_level'] == 'add_SA' \
            or user_data['high_level'] == 'change_product_api' and user_data['main_product'] == 'Other'  \
                and user_data['product_features_other'] == 'None/other' and user_data['confidentiality'] == 'Yes' \
            or user_data['high_level'] == 'change_product_api' and user_data['main_product'] == 'Other'  \
                and user_data['product_features_other'] == 'None/other' and user_data['confidentiality'] == 'Not sure' \
            or user_data['high_level'] == 'change_product_api' and user_data['main_product'] == 'Other'  \
                and user_data['product_features_other'] == 'None/other' and user_data['confidentiality'] == 'No' \
            and user_data['integrity'] == 'Yes' \
            or user_data['high_level'] == 'change_product_api' and user_data['main_product'] == 'Other'  \
                and user_data['product_features_other'] == 'None/other' and user_data['confidentiality'] == 'No' \
            and user_data['integrity'] == 'Not sure' \
            or user_data['high_level'] == 'change_product_api' and user_data['main_product'] == 'Other'  \
                and user_data['product_features_other'] == 'None/other' and user_data['confidentiality'] == 'No' \
            and user_data['integrity'] == 'No' and user_data['availability'] == 'Yes' \
            or user_data['high_level'] == 'change_product_api' and user_data['main_product'] == 'Other'  \
                and user_data['product_features_other'] == 'None/other' and user_data['confidentiality'] == 'No' \
            and user_data['integrity'] == 'No' and user_data['availability'] == 'Not sure' \
            or user_data['high_level'] == 'change_product_ui' \
                and user_data['product_ui_question_change'] \
            in ['change_ui_url_inputs', 'change_ui_load_active_content', 'change_ui_change_dom'] \
            or user_data['high_level'] == 'change_product_api' \
                and user_data['main_product'] \
            in ['Changing or adding an API endpoint that processes XML files from user input', 'Introducing/changing a file upload feature', 'Making use of Cryptography'] \
            or user_data['high_level'] == 'change_infrastructure' \
                and user_data['infrastructure_gcp'] \
            in ['Access control change that involves granting privileged or public access to an entity.', 'Changing an existing firewall rule or adding a new one', 'Changing logging configs'] \
                and user_data['if_access_control_change_playbook'] == 'Not sure':
            logging.info(
                "User %s submitted a HIGH Risk JIRA Ticket", user_email)
            if 'jira_ticket_link' in user_data:
                slacknotify.slacknotify_jira_ticket_risk_assessment(
                    jtra_slack_channel, user_data['jira_ticket_link'], user_email, user_data)
            else:
                slacknotify.slacknotify_jira_ticket_risk_assessment(
                    jtra_slack_channel, user_data['context'], user_email, user_data)
        else:
            logging.info(
                "User %s submitted a MEDIUM/LOW Risk Jira Ticket", user_email)
        return ''
    except Exception as error:
        error_message = f"Exception /submitJTRA enspoint: {error}"
        logging.warning(error_message)
        slacknotify.slacknotify_jira_ticket_risk_assessment_error(
            jtra_slack_channel, user_email, user_data)
        status_code = 404
        message = """
            There is something wrong with the input! Server did not respond correctly to your request! 
            """
        return Response(json.dumps({'statusText': message}), status=status_code, mimetype='application/json')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', 8080)))
