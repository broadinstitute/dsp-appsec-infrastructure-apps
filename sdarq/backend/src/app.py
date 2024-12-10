"""
This module
- sends a new service & app requirements request
        - creates a new product in Defect Dojo
        - creates a Jira Ticket in AppSec board
        - notifies AppSec Slack channel about service/app requirements request
        - creates a new security controls template for a new service/product
- sends request to scan a GCP project against the CIS Benchmark
- get results from BigQuery for a scanned GCP project
- send a request for threat model
- send a request for security pentest
- scan a service via ZAP tool
- add security controls for a service
- edit security controls for a service
- list all security controls for all services
- list security controls for a services
- calculates the risk of a Jira ticket and notifies AppSec team
"""
#!/usr/bin/env python3

import json
import logging
import os
import re
import threading
from typing import List
from urllib.parse import urlparse

import dojo_helper
import google.cloud.logging
import jiranotify
import jsonschema
import parse_data as parse_json_data
import requests
import slacknotify
from flask import Flask, Response, jsonify, request
from flask_cors import cross_origin
from google.cloud import bigquery, firestore, pubsub_v1
from jsonschema import validate
from schemas.cis_scan_schema import cis_scan_schema
from schemas.edit_security_controls_schema import edit_security_controls_schema
from schemas.manual_pentest_request_schema import mp_schema
from schemas.new_app_schema import new_app_schema
from schemas.new_service_schema import new_service_schema
from schemas.security_controls_schema import security_controls_schema
from schemas.threat_model_request_schema import tm_schema
from schemas.zap_scan_schema import zap_scan_schema
from security_headers import security_headers
from trigger import parse_tags
from authz_decorator import iap_group_authz
from iap_userinfo import validate_iap_jwt

dojo_host = os.getenv('dojo_host')
dojo_api_key = os.getenv('dojo_api_key')
sdarq_host = os.getenv('sdarq_host')
dojo_host_url = os.getenv('dojo_host_url')
appsec_slack_channel = os.getenv('appsec_slack_channel')
appsec_sdarq_error_channel = os.getenv('appsec_sdarq_error_channel')
appsec_jira_project_key = os.getenv('appsec_jira_project_key')
jtra_slack_channel = os.getenv('jtra_slack_channel')
jira_instance = os.getenv('jira_instance')
firestore_collection = os.environ['CIS_FIRESTORE_COLLECTION']
cis_topic_name = os.environ['CIS_JOB_TOPIC']
pubsub_project_id = os.environ['PUBSUB_PROJECT_ID']
zap_topic_name = os.environ['ZAP_JOB_TOPIC']
security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']
iap_allowlist = os.getenv('IAP_ALLOWLIST', '')
iap_allowlist_final = iap_allowlist.split(",")


headers = {
    "content-type": "application/json",
    "Authorization": f"Token {dojo_api_key}",
}
# configure logging
loggingclient = google.cloud.logging.Client()
loggingclient.setup_logging()

app = Flask(__name__)

client = bigquery.Client()

db = firestore.Client()


@app.after_request
def add_security_headers(response):
    """
    Adds security headers listed in security_headers.py
    """
    for header, value in security_headers.items():
        response.headers[header] = value
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
    status = {'statusText': 'Service is healthy'}
    return jsonify(status), 200


@app.route('/user-details/', methods=['GET'])
@cross_origin(origins=sdarq_host)
def user_details():
    """
    Returns the email and group from IAP.
    """
    user_id, user_email, error_str = validate_iap_jwt()
    if user_email is None:
        return jsonify({'error': 'Missing email in the request headers'}), 400
    
    if parse_json_data.parse_user_email(user_email) in iap_allowlist_final:
        return jsonify({'statusText': 'User has the right permission', 'verified': True}), 200
    else:
        return jsonify({'statusText': 'Access is denied, this user is not authorized', 'verified': False}), 403


@app.route('/submit/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def submit():
    """
    Create new product to DefectDojo,
    create Jira ticket in teams board (optional),
    create Jira ticket in appsec team board for TM, 3rd party dependecies scan and SAST
    Args:
        Json data
    Returns:
        200 status
        400 status
    """

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    try:
        json_data = request.get_json()
        dojo_name = json_data['Service']
        security_champion = json_data['Security champion']
        product_type = 1
        user_email = request.headers.get('X-Goog-Authenticated-User-Email')

        architecture_diagram = json_data['Architecture Diagram']
        github_url = json_data['Github URL']
        appsec_jira_ticket_description = github_url + '\n' + architecture_diagram
        appsec_jira_ticket_summury_tm = 'Threat Model request ' + dojo_name
        appsec_jira_ticket_summury_srcl = 'Add ' + \
            dojo_name + ' to 3rd party dependencies scan tool'
        appsec_jira_ticket_summury_sast = 'Add ' + dojo_name + ' to a SAST tool'
        appsec_jira_ticket_summury_dast = 'Add ' + dojo_name + ' to DAST tool'
        project_key_id = json_data['JiraProject']
        dev_jira_ticket_summury_alerts = dojo_name + ' security related requirements'
        app_jira_ticket_summury_alerts = 'Track ' + \
            dojo_name + ' security related requirements'
        jira_description = json.dumps(
            json_data['Ticket_Description']).strip('[]')

        validate(instance=json_data, schema=new_service_schema)

        formatted_jira_description = jira_description.strip('", "').replace('", "', '\n-')

        del json_data['Ticket_Description']

        product_id = dojo_helper.dojo_create_or_update(dojo_name, parse_json_data.prepare_dojo_input(json_data), product_type, user_email, appsec_slack_channel, security_champion, dojo_host_url)

        setSecConDDlink = db.collection(security_controls_firestore_collection).document(
            dojo_name.lower())
        doc = setSecConDDlink.get()
        if bool(doc.to_dict()) is True:
            setSecConDDlink.set({
                u'defect_dojo': '{0}/product/{1}'.format(dojo_host_url, str(product_id))
            }, merge=True)

        ticket_data = [
            (app_jira_ticket_summury_alerts, formatted_jira_description),
            (appsec_jira_ticket_summury_tm, appsec_jira_ticket_description),
            (appsec_jira_ticket_summury_srcl, appsec_jira_ticket_description),
            (appsec_jira_ticket_summury_sast, appsec_jira_ticket_description),
            (appsec_jira_ticket_summury_dast, appsec_jira_ticket_description)
        ]
            
            
        for summary, description in ticket_data:
            jiranotify.create_board_ticket(appsec_jira_project_key, summary, description)

        jiranotify.create_board_ticket(
            project_key_id,
            dev_jira_ticket_summury_alerts,
            formatted_jira_description)

        return ''
    except Exception as error:
        error_message = f"Exception /submit endpoint: {error}"
        slacknotify.slacknotify_error_submit_endpoint(error, appsec_sdarq_error_channel, user_email, dojo_name)
        logging.warning(error_message)
        message = """
        There is something wrong with the input! Server did not respond correctly to your request!
        """
        return jsonify({'statusText': message}), 400


@app.route('/submit_new_app/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def submit_app():
    """
    Create new product to DefectDojo,
    create Jira ticket in teams board (optional),
    create Jira ticket in appsec team board for TM, 3rd party dependecies scan and SAST
    Args:
        Json data
    Returns:
        200 status
        400 status
    """

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400


    try:
        json_data = request.get_json()
        dojo_name = json_data['Service']
        security_champion = json_data['Security champion']
        product_type = 1
        user_email = request.headers.get('X-Goog-Authenticated-User-Email')

        architecture_diagram = json_data['Architecture Diagram']
        github_url = json_data['Github URL']
        appsec_jira_ticket_description = github_url + '\n' + architecture_diagram
        appsec_jira_ticket_summury_tm = 'Threat Model request ' + dojo_name
        appsec_jira_ticket_summury_dast = 'Add ' + dojo_name + ' to DAST tool'
        appsec_jira_ticket_summury_srcl = 'Add ' + \
            dojo_name + ' to 3rd party dependencies scan tool'
        appsec_jira_ticket_summury_sast = 'Add ' + dojo_name + ' to a SAST tool'
        project_key_id = json_data['JiraProject']
        dev_jira_ticket_summury_alerts = dojo_name + ' security requirements'
        appsec_jira_ticket_summury_alerts = 'Track ' + \
            dojo_name + ' security requirements'

        jira_description = json.dumps(
            json_data['Ticket_Description']).strip('[]')

        validate(instance=json_data, schema=new_app_schema)

        formatted_jira_description = jira_description.strip(
            '", "').replace('", "', '\n-')

        del json_data['Ticket_Description']

        product_id = dojo_helper.dojo_create_or_update(dojo_name, parse_json_data.prepare_dojo_input(json_data), product_type, user_email, appsec_slack_channel, security_champion, dojo_host_url)

        setSecConDDlink = db.collection(
            security_controls_firestore_collection).document(dojo_name.lower())
        doc = setSecConDDlink.get()
        if bool(doc.to_dict()) is True:
            setSecConDDlink.set({
                u'defect_dojo': '{0}/product/{1}'.format(dojo_host_url, str(product_id))
            }, merge=True)


        ticket_data = [
            (appsec_jira_ticket_summury_alerts, formatted_jira_description),
            (appsec_jira_ticket_summury_tm, appsec_jira_ticket_description),
            (appsec_jira_ticket_summury_srcl, appsec_jira_ticket_description),
            (appsec_jira_ticket_summury_sast, appsec_jira_ticket_description),
            (appsec_jira_ticket_summury_dast, appsec_jira_ticket_description)
        ]
            
        for summary, description in ticket_data:
            jiranotify.create_board_ticket(appsec_jira_project_key, summary, description)

        jiranotify.create_board_ticket(
            project_key_id,
            dev_jira_ticket_summury_alerts,
            formatted_jira_description)

        return ''
    except Exception as error:
        error_message = f"Exception /submit_new_app endpoint: {error}"
        slacknotify.slacknotify_error_submit_endpoint(error, appsec_sdarq_error_channel, user_email, dojo_name)
        logging.warning(error_message)
        message = """
        There is something wrong with the input! Server did not respond correctly to your request!
        """
        return jsonify({'statusText': message}), 400

@app.route('/cis_results/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def cis_results():
    """
    Get CIS results for a specific google project
    Args:
        project_id: GCP project that will be scanned for security configurations
    Returns:
      200 status -> json: Security scan results for given project_id
      400 status
    """
    project_id_encoded = request.get_data()
    project_id = project_id_encoded.decode("utf-8")
    pattern = "^[a-z0-9][a-z0-9-_]{4,42}[a-z0-9]$"
    project_id_edited = project_id.strip('-').replace('-', '_')
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    logging.info(
        "Request by %s to read CIS scanner results for project %s ",
        user_email,
        project_id_edited)

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

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
                        "last_modified_datetime",
                        "STRING",
                        last_modified_datetime)])
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
            error_message = f"Exception /cis_results endpoint: {error}"
            slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
            logging.warning(error_message)
            notfound = """
            This Google project is not found! Did you make sure to supply the right GCP Project ID? Please check again!
            """
            return jsonify({'statusText': notfound}), 404
    else:
        message = """
        Your GCP project_id is not valid! Enter a valid value!
        """
        return jsonify({'statusText': message}), 400


@app.route('/cis_scan/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def cis_scan():
    """
    Scans a specific google project
    Args: Project_id (json data)
    Return:
        200 status
        400 status
    """
    json_data = request.get_json()
    user_project_id = json_data['project_id']
    pattern = "^[a-z0-9][a-z0-9-_]{4,42}[a-z0-9]$"
    message = ""
    results_url = f"{sdarq_host}/gcp-project-security-posture/results?project_id={user_project_id}"
    message = message.encode("utf-8")
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    if re.match(pattern, user_project_id):
        try:
            validate(instance=json_data, schema=cis_scan_schema)
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(
                pubsub_project_id, cis_topic_name)
            user_proj = user_project_id.replace('-', '_')
            logging.info(
                "Request by %s to assess security posture for project %s ",
                user_email,
                user_proj)
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

            def on_snapshot(
                    doc_snapshots: List[firestore.DocumentSnapshot], _changes, _read_time):
                for doc in doc_snapshots:
                    if doc.exists:
                        callback_done.set()
                        return

            user_proj = user_project_id.replace('-', '_')
            doc_ref = db.collection(firestore_collection).document(user_proj)
            doc_ref.delete()
            doc_watch = doc_ref.on_snapshot(on_snapshot)
            callback_done.wait(timeout=7200)
            doc_watch.unsubscribe()
            doc = doc_ref.get()

            check_dict = doc.to_dict()
            if check_dict:
                text_message = check_dict['Error']
                doc_ref.delete()
                return jsonify({'statusText': text_message}), 404
            else:
                doc_ref.delete()
                return jsonify({'statusText': 'Scan run successfully!'}), 200
        except Exception as error:
            error_message = f"Exception /cis_scan endpoint: {error}"
            logging.warning(error_message)
            slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
            message = """
            There is something wrong with the input! Server did not respond correctly to your request!
            """
            return jsonify({'statusText': message}), 400
    else:
        message = """
        Your GCP project_id is not valid! Enter a valid value!
        """
        return jsonify({'statusText': message}), 400


@app.route('/request_tm/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def request_tm():
    """
    Creates a request for a threat model for a specific service
    Creates a Jira ticket and notifies the team in Slack
    Args:
        request: Flask request object containing JSON data supplied by user
    Returns:
        Response object with 200 status if successful, or 400 status if there was an error
    """
    user_data = request.get_json()
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    try:
        validate(instance=user_data, schema=tm_schema)
        request_type = user_data['Type']
        project_name = user_data['Name']
        logging.info("Threat model request for %s by %s",
                     project_name, user_email)

        jira_ticket_summary = f"{request_type} {project_name}"
        jira_ticket_description = '\n'.join(
            [user_data['Diagram'], user_data['Document'], user_data['Github']])

        jira_ticket_appsec = jiranotify.create_board_ticket(
            appsec_jira_project_key, jira_ticket_summary, jira_ticket_description)
        logging.info(
            "Jira ticket created in appsec board for %s threat model", project_name)

        slacknotify.slacknotify_threat_model(appsec_slack_channel, user_email, request_type,
                                             project_name, jira_instance, jira_ticket_appsec, appsec_jira_project_key)

        return Response(status=200)

    except jsonschema.ValidationError as e:
        error_message = "Validation error in /request_tm endpoint!"
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        return jsonify({'statusText': error_message}), 400

    except Exception as e:
        error_message = f"Exception in /request_tm endpoint: {e}"
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        return jsonify({'statusText': 'There was an exception!'}), 400


@app.route('/zap_scan/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def zap_scan():
    """
    Scan a service via ZAP tool
    Args:
        Json file
    Returns:
        200 status if a Zap Scan is triggered
        404 status if project not found
    """
    json_data = request.get_json()
    message = b""
    endpoint = f"{dojo_host}api/v2/endpoints?tag=scan&limit=1000"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    text_message = """
                    You should NOT run a security pentest against the URL you entered,
                    or maybe it doesn't exist in AppSec list. Please contact AppSec team.
                    """
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

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
                service_codex_project, default_slack_channel, service_scan_type, product_id = parse_tags(
                    endpoint)
                if endpoint['path'] is None:
                    service_full_endpoint = f"{endpoint['protocol']}://{endpoint['host']}"
                else:
                    if endpoint['path'].strip(
                            '/') == parsed_user_url.path.strip('/'):
                        service_full_endpoint = f"{endpoint['protocol']}://{endpoint['host']}/{endpoint['path']}"
                    else:
                        logging.info(
                            "User %s requested to scan via ZAP a service that does not exist in DefectDojo endpoint list",
                            user_email)
                        return jsonify( {'statusText': text_message}), 404

                # Adds job to pubsub to be picked up by the zap scan code.
                # CodeDx project is set to an empty string to prevent overwriting reports
                # The severities field was only used to generate CodeDx reports.
                publisher.publish(zap_topic_path,
                                  data=message,
                                  URL=service_full_endpoint,
                                  CODEDX_PROJECT="",
                                  SCAN_TYPE=service_scan_type.name,
                                  SLACK_CHANNEL=dev_slack_channel,
                                  PRODUCT_ID=product_id)
                logging.info("User %s requested to scan via ZAP %s service",
                             user_email, service_full_endpoint)
                return ''
        else:
            logging.info(
                "User %s requested to scan via ZAP a service that does not exist in DefectDojo endpoint list",
                user_email)
            return jsonify( {'statusText': text_message}), 404
    except Exception as error:
        error_message = f"Exception /zap_scan enspoint: {error}"
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        message = """
        There is something wrong with the input! Server did not respond correctly to your request!
        """
        return jsonify({'statusText': message}), 400


@app.route('/create_sec_control_template/', methods=['POST'])
@iap_group_authz(iap_allowlist_final)
@cross_origin(origins=sdarq_host)
def create_sec_control_template():
    """
    Store data to Firestore
    Args: Provided json data from user
    Returns: 200 status if data stored to Firestore
             400 status if input is invalid/ service already exists
    """
    user_input = request.get_json()
    service_name = user_input['service']
    pattern = "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    if not re.match(pattern, service_name):
        message = """
        Invalid input! Please make sure you include numbers, -, _ and alphabetical characters.
        """
        logging.info(
            "User %s requested to create SCT for a service, but INVALID input was provided",
            user_email)
        return jsonify({'statusText': message}), 400

    try:
        validate(instance=user_input, schema=security_controls_schema)
        service_doc_ref = db.collection(security_controls_firestore_collection).document(
            service_name.lower())
        if service_doc_ref.create(user_input):
            message = "A new security controls template is created!"
            logging.info(
                "A new security controls template is created by %s",
                user_email)
            return jsonify({'statusText': message}), 200
        else:
            message = """
            This service already exists, if you want to edit it, go to the edit page.
            """
            logging.info(
                "User %s requested to create SCT for a service, but it already exists",
                user_email)
            return jsonify({'statusText': message}), 400
    except Exception as error:
        error_message = f"Exception /create_sec_controls_template endpoint: {error}"
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        message = """
        There is something wrong with the input! Server did not respond correctly to your request!
        """
        return jsonify({'statusText': message}), 400


@app.route('/edit_sec_controls/', methods=['PUT'])
@iap_group_authz(iap_allowlist_final)
@cross_origin(origins=sdarq_host)
def edit_sec_controls():
    """
    Edit data for a specific service
    Args: Provided json data from user
    Returns: 200 status if data stored to Firestore
             400 status if input is invalid/service does not exist
    """
    json_data = request.get_json()
    service_name = json_data['service']
    pattern = "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    if re.match(pattern, service_name):
        try:
            validate(instance=json_data, schema=edit_security_controls_schema)
            doc_ref = db.collection(security_controls_firestore_collection).document(
                service_name.lower())
            doc = doc_ref.get()
            if bool(doc.to_dict()) is True:
                for key in json_data:
                    doc_ref.set({
                        f'{key}': json_data[key]
                    }, merge=True)
                    logging.info(
                        "Security control %s for the choosen service have changed by %s !",
                        key, user_email)
                return ''
            else:
                message = """
                This service does not exist!
                """
                logging.info(
                    "User %s requested to edit a service security controls, but this service does not exist!",
                    user_email)
                return jsonify({'statusText': message}), 404
        except Exception as error:
            error_message = f"Exception /edit_sec_controls endpoint: {error}"
            slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
            logging.warning(error_message)
            message = """
            There is something wrong with the input! Server did not respond correctly to your request!
            """
            return jsonify({'statusText': message}), 400
    else:
        message = """
        Invalid input! Please make sure you include numbers, -, _ and alphabetical characters.
        """
        logging.info(
            "User %s requested to edit SCT for a service, but INVALID input was provided",
            user_email)
        return jsonify({'statusText': message}), 400


@app.route('/delete_service_sec_controls/', methods=['POST'])
@iap_group_authz(iap_allowlist_final)
@cross_origin(origins=sdarq_host)
def delete_service_sec_controls():
    """
    Delete security controls for a service
    Args: Provided json data from user
    Returns: 200 status if data remove successfully
             404 if service not found
             400 is there is an error
    """
    json_data = request.get_json()
    service_name = json_data['service']
    pattern = "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400
    
    if re.match(pattern, service_name):
        try:
            validate(instance=json_data, schema=edit_security_controls_schema)
            doc_ref = db.collection(security_controls_firestore_collection).document(
                service_name.lower())
            doc = doc_ref.get()
            if bool(doc.to_dict()) is True:
                db.collection(security_controls_firestore_collection).document(service_name.lower()).delete()
                logging.info("Security control %s for the choosen service are removed by %s !",
                        service_name, user_email)
                return ''
            else:
                message = """
                This service does not exist!
                """
                logging.info(
                    "User %s requested to remove service security controls, but this service does not exist!",
                    user_email)
                return jsonify({'statusText': message}), 404
        except Exception as error:
            error_message = f"Exception /delete_service_sec_controls endpoint: {error}"
            slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
            logging.warning(error_message)
            message = """
            There is something wrong with the input! Server did not respond correctly to your request!
            """
            return jsonify({'statusText': message}), 400
    else:
        message = """
        Invalid input! Please make sure you include numbers, -, _ and alphabetical characters.
        """
        logging.info(
            "User %s requested to remove Security Controls for a service, but INVALID input was provided",
            user_email)
        return jsonify({'statusText': message}), 400


@app.route('/get_sec_controls/', methods=['GET'])
@cross_origin(origins=sdarq_host)
def get_sec_controls():
    """
    Get all data from Firestore
    Returns:
        200 status
        400 status
    """
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    user_email = request.headers.get('X-Goog-Authenticated-User-Email')
    security_controls = []

    try:
        docs = db.collection(security_controls_firestore_collection).stream()
        for doc in docs:
            security_controls.append(doc.to_dict())
        logging.info('User %s read security controls for the list of services.', user_email)
        return jsonify(security_controls)
    except Exception as error:
        error_message = "Server can't get security controls! Contact AppSec team for more information."
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(f"Exception /get_sec_controls endpoint: {error}")
        return jsonify({'statusText': error_message}), 400


@app.route('/get_sec_controls_service/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def get_sec_controls_service():
    """
    Get all security controls for a service
    Args: Service name (Json format)
    Returns: 200 status (Json data)
             404 status if project not found
             400 if error occurred
    """
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    json_data = request.get_json()
    service_name = json_data.get('service')

    if not service_name or not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$', service_name):
        message = 'Please enter a valid value for your service name! Contact team for more information.'
        logging.info('User %s did not provide a valid value for the service name to read security controls.', user_email)
        return jsonify({'statusText': message}), 400

    try:
        service_name_lowercase = service_name.lower()
        doc_ref = db.collection(security_controls_firestore_collection).document(service_name_lowercase)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify(doc.to_dict())
        else:
            message = 'This service does not exist!'
            logging.info('User %s requested to read security controls of a service that does not exist.', user_email)
            return jsonify({'statusText': message}), 404

    except firestore.exceptions.InvalidArgument:
        message = 'Invalid service name. Please enter a valid service name.'
        logging.warning('User %s provided an invalid service name: %s', user_email, service_name)
        return jsonify({'statusText': message}), 400

    except Exception as error:
        error_message = f'Exception /get_sec_controls_service endpoint: {error}'
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        message = 'Server can\'t get security controls! Contact AppSec team for more information.'
        return jsonify({'statusText': message}), 400



@app.route('/request_manual_pentest/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def request_manual_pentest():
    """
    Creates a request for security pentest for a specific service
    Creates a Jira ticket and notifies team in Slack
    Args:
        request: Flask request object containing JSON data supplied by user
    Returns:
        Response object with 200 status if successful, or 400 status if there was an error
    """
    user_data = request.get_json()
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400

    try:
        validate(instance=user_data, schema=mp_schema)
        project_name = user_data['service']
        appsec_jira_ticket_summury = 'Security pentest request for ' + \
            user_data['service']
        appsec_jira_ticket_description = 'URL to pentest: ' + user_data['URL'] + \
            '\n' + 'Environment: ' + user_data['env'] + \
            '\n' + 'Permission levels:' + user_data['permission_level'] + \
            '\n' + 'Documentation: ' + user_data['document'] + \
            '\n' + 'Security champion: ' + user_email

        jira_ticket_appsec = jiranotify.create_board_ticket(
            appsec_jira_project_key,
            appsec_jira_ticket_summury,
            appsec_jira_ticket_description)

        logging.info(
            "Jira ticket created in appsec board for %s security pentest request by %s",
            project_name,
            user_email)

        slacknotify.slacknotify_security_pentest(appsec_slack_channel,
                                                 user_email,
                                                 project_name,
                                                 jira_instance,
                                                 jira_ticket_appsec,
                                                 appsec_jira_project_key)
        return Response(status=200)

    except jsonschema.ValidationError as e:
        error_message = "Validation error in /request_manual_pentest endpoint!"
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        return jsonify({'statusText': error_message}), 400 
    
    except Exception as e:
        error_message = f"Exception for /request_manual_pentest endpoint: {e}"
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        return jsonify({'statusText': 'There was an exception!'}), 400


@app.route('/submit_jtra/', methods=['POST'])
@cross_origin(origins=sdarq_host)
def submit_jtra():
    """
    Calculates the risk based on the user data and notifies AppSec team for the review
    Args:
        JSON data supplied by user
    Returns:
        200 status
        400 status
    """
    user_data = request.get_json()
    user_email = request.headers.get('X-Goog-Authenticated-User-Email')

    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'statusText': 'Bad Request'}), 400
    try:
        if user_data['high_level'] == 'add_SA' \
            or user_data['high_level'] == 'phi' \
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
                    jtra_slack_channel,
                    user_data['jira_ticket_link'],
                    user_email,
                    user_data,
                    user_data['AppSec_due_date'])
            else:
                slacknotify.slacknotify_jira_ticket_risk_assessment(
                    jtra_slack_channel,
                    user_data['context'],
                    user_email,
                    user_data,
                    user_data['AppSec_due_date'])
            status = {'statusText': 'The risk for this ticket is HIGH!  Please contact AppSec team if you have any questions!'}
            return jsonify(status), 200
        else:
            logging.info(
                "User %s submitted a MEDIUM/LOW Risk Jira Ticket", user_email)
            status = {'statusText': 'The risk for this ticket is MEDIUM/LOW!  Please contact AppSec team if you have any questions!'}
            return jsonify(status), 200
    except Exception as error:
        error_message = f"Exception /submitJTRA enspoint: {error}"
        slacknotify.slacknotify_error_endpoint(error_message, appsec_sdarq_error_channel, user_email)
        logging.warning(error_message)
        slacknotify.slacknotify_jira_ticket_risk_assessment_error(
            jtra_slack_channel, user_email, user_data)
        message = """
            There is something wrong with the input! Server did not respond correctly to your request!
            """
        return jsonify({'statusText': message}), 400


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', 8080)))
