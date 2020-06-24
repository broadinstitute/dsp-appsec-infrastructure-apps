#!/usr/bin/env python3
import requests 
import csv, io
import json

def github_action_trigger(github_token, github_org, repo, event, json_data):
    """
    Triggers a Github Action Workflow

    Args:
        github_token: Github token to trigger workflow
        github_org: Github repo organization
        repo: Github repo name 
        event: Workflow event to trigger
        json_data: Service data from sdarq

    Returns:
        Triggers Github action
    """
    csv_headers = [
        "Session",
        "Name",
        "POC for Sheet",
        "Business Name",
        "Status",
        "Area",
        "Capabilities",
        "Fit to purpose",
        "Could we buy?",
        "Deployment",
        "Language",
        "HTTP FW",
        "Persistence FW",
        "DB / Data Stores",
        "Testing FW",
        "CI Tool",
        "Integration Testing",
        "Release",
        "NR App Monitoring",
        "Alerts",
        "Dependent Services",
        "Repo",
        "Dojo",
        "SC",
        "Codacy",
        "Production URL",
        "API Docs",
        "Production Google Project",
        "Playbook"
    ]

    service_data = dict.fromkeys(csv_headers)
    service_data["Name"] = json_data["Service"]
    service_data["Capabilities"] = json_data["Description"]
    service_data["Repo"] = json_data["Github URL"]
    service_data["Production Google Project"] = json_data["Google project"]
    service_data["Deployment"] = json_data["Architecture"]

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(service_data.values())
    service_data_csv = si.getvalue()

    endpoint = "https://api.github.com/repos/{}/{}/dispatches".format(github_org, repo)
    headers = {
        "Accept": "application/vnd.github.everest-preview+json",
        "Authorization": "token {}".format(github_token)
    }

    client_payload = {
        "name": service_data["Name"],
        "data": service_data_csv
    }

    data = {
        "event_type": event, 
        "client_payload": client_payload
    }

    response = requests.post(url = endpoint, data = json.dumps(data), headers = headers)
