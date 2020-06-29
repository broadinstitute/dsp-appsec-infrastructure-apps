#!/usr/bin/env python3
import requests
import json

def github_repo_dispatcher(github_token, github_org, github_repo, github_event, json_data):
    """Triggers a Github Action Workflow

    Args:
        github_token: Github token to trigger workflow
        github_org: Github repo organization
        github_repo: Github repo name
        github_event: Workflow event to trigger
        json_data: Service data from sdarq

    Returns:
        Triggers Github action
    """

    endpoint = "https://api.github.com/repos/{}/{}/dispatches".format(github_org, github_repo)
    headers = {
        "Accept": "application/vnd.github.everest-preview+json",
        "Authorization": "token {}".format(github_token)
    }

    client_payload = {
        "data": json_data
    }

    data = {
        "event_type": github_event,
        "client_payload": client_payload
    }

    requests.post(url = endpoint, data = json.dumps(data), headers = headers)
