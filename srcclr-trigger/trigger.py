import json
import logging
import re
from enum import Enum
from os import getenv
from typing import List, TypedDict
from urllib.parse import urlparse

import requests


class Workspace(str, Enum):
    """
    Sourceclear workspaces
    """

    dsde = "DSDE"
    kdux = "KDUX"

    def __str__(self):
        return str(self.name).lower()

    def label(self):
        """"Get user-friendly name of the scan type"""
        return str(self.value)


class Environment(str, Enum):
    """
    Sourceclear workspaces
    """

    PYTHON3 = "python:3.8-buster"
    SCALA = "mozilla/sbt"
    GRADLEJAVA11 = "gradle:7.1.0-jdk11"
    NODE12 = "node:12-buster"

    def __str__(self):
        return str(self.name).lower()

    def label(self):
        """"Get user-friendly name of the scan type"""
        return str(self.value)


class SrcclrEngagement(TypedDict):
    """
    Defines a Sourceclear engagement
    """
    org: str
    repo: str
    branch: str
    subdir: str
    workspace: Workspace
    env: Environment


def parse_engagements(results: List) -> List[SrcclrEngagement]:
    engagements = []
    for engagement in results:
        sc_eng: SrcclrEngagement = {}
        for tag in engagement['tags']:
            tag_match = TAG_MATCHER.match(tag)
            if not tag_match:
                continue
            tag_key, tag_val = tag_match.group(1), tag_match.group(2)
            if tag_key == "workspace":
                sc_eng["workspace"] = Workspace[tag_val.lower()].value
            if tag_key == "environment":
                sc_eng["env"] = Environment[tag_val.upper()].value
            if tag_key == "action_repo":
                sc_eng["action_repo"] = Environment[tag_val.upper()].value

        if not sc_eng["workspace"]:
            logging.error("No workspace tag found.")
            continue

        if not sc_eng["env"]:
            logging.error("No environment tag found.")
            continue

        try:
            sections = urlparse(engagement["source_code_management_uri"]).path[1:].split('/')
            sc_eng["org"] = sections.pop(0)
            sc_eng["repo"] = sections.pop(0)
            sc_eng["subdir"] = ''.join(sections)
        except:
            logging.error("Trouble parsing Github URL")
            continue

        sc_eng["branch"] = engagement['branch_tag']
        
        print(sc_eng)
        engagements.append(sc_eng)

    return engagements

TAG_MATCHER = re.compile(r"^([^:]+):(.*)$")

def get_defect_dojo_engagements(base_url: str, api_key: str) -> List:
    """
    Fetch projects from DefectDojo.
    """
    endpoint = base_url + "/api/v2/engagements/?tags=sourceclear"
    headers = {
        "content-type": "application/json",
        "Authorization": f"Token {api_key}",
    }
    res = requests.get(endpoint, headers=headers, timeout=30)
    res.raise_for_status()
    engagements = parse_engagements(res.json()["results"])
    return engagements


def send_repo_dispatches(engagements: List[SrcclrEngagement], dispatch_destination: str, repo_token: str):
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {repo_token}",
    }
    for engagement in engagements:
        gh = engagement["action_repo"]
        repo_url = f"https://api.github.com/repos/{ gh }/dispatches"
        data = {
            'event_type': 'srcclr',
            'client_payload': engagement
        }
        json_data = json.dumps(data)
        res = requests.post(
            f"https://api.github.com/repos/{dispatch_destination}/dispatches",
            data=json_data,
            headers=headers
        )
        res.raise_for_status()

def main():
    """
    - Fetch the list of endpoints from DefectDojo
    - Trigger the scans for all endpoints
    """
    defect_dojo_url = getenv("DEFECT_DOJO_URL")
    defect_dojo_key = getenv("DEFECT_DOJO_KEY")
    repo_token = getenv("REPO_TOKEN")

    engagements = get_defect_dojo_engagements(defect_dojo_url, defect_dojo_key)
    send_repo_dispatches(engagements, repo_destination, repo_token)


if __name__ == "__main__":
    main()
