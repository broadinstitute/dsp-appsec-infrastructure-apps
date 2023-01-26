"""Update SAST security-controls data."""

import logging
import os
import re

import requests
from google.cloud import firestore
from requests.auth import HTTPBasicAuth

SECURITY_CONTROLS = os.environ['SC_FIRESTORE_COLLECTION']
SAST_DETAILS = os.environ['SAST_FIRESTORE_COLLECTION']
GITHUB_GQL_ENDPOINT = "https://api.github.com/graphql"
fs = firestore.Client()

CODACY_BASE = "https://app.codacy.com/api/v3"
CODACY_API_KEY=os.getenv("CODACY_API_KEY")
SONARCLOUD_API_KEY=os.getenv("SONARCLOUD_API_KEY")
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN")

repo_re = re.compile(r'https://github.com/([a-zA-Z0-9\-_]+)/([a-zA-Z0-9\-_]+)')

SONAR_ORGS = {
    "broadinstitute": "dsp-appsec",
    "DataBiosphere": "broad-databiosphere",
    "CancerDataAggregator": "cancerdataaggregator"
}

CODACY_ORGS = [
    "DataBiosphere",
    "broadinstitute"
]

CODACY = "Codacy"
SONAR = "SonarCloud"
GITHUB = "GitHub"

RepoKey = tuple[str, str] # organization, repository
Repo = dict[str, object] # key is source e.g. CODACY, GITHUB; value is repo info from source
Repos = dict[RepoKey, Repo]
CodacyOrgData = dict[str, list] # {"org": [ user_suggestion, ... ]}


def repo_list_from_security_controls(repos: Repos):
    """Iniitalize repos from Firestore."""
    # sc_collection = fs.collection(security_controls_firestore_collection)
    # sc_docs = sc_collection.stream()
    # for doc in sc_docs:
    #     project = doc.to_dict()
    #     logging.debug(f"github {g(project,'github')}
    # sast {g(project,'sast')} link {g(project,'sast_link')}")

    get_repo(repos, ('broadinstitute', 'dsp-appsec-infrastructure-apps'))
    get_repo(repos, ('DataBiosphere', 'terra-ui'))

def list_github(repos: Repos):
    '''Get GitHub metadata for all repos.'''
    count = 0
    for org, repo_name in repos.keys():
        list_repo_info(repos, org, repo_name)
        count += 1
        if count > 500:
            break

def quote(name: str) -> str:
    '''Enclose string in escaped double quotes.'''
    return r'\"' + name + r'\"'

def body(gql: str, params: dict) -> str:
    '''Expand parameters and wrap gql in JSON.'''
    gql = gql.replace('\n',' ')
    for key, value in params.items():
        gql = gql.replace("$" + key, quote(value))
    return '{ "query": "' + gql + '" }'

def list_repo_info(repos: Repos, org, repo_name):
    '''Pull GitHub metadata on this repo.'''

    logging.info(f"GitHub {repo_name} {org}")
    headers = {
        "Authorization": f"bearer {GITHUB_TOKEN}"
    }

    gql = '''
            query {
                repository(name: $repo_name, owner: $org) {
                    visibility
                    isArchived
                    primaryLanguage {
                        name
                    }
                }
            }
    '''
    github_r = requests.post(GITHUB_GQL_ENDPOINT,
        body(gql, {'repo_name':repo_name, 'org':org}),
        headers=headers, timeout=5)
    github = github_r.json()

    github_repo = github['data']['repository']
    record = {}
    record['private'] = (github_repo['visibility'] != "PUBLIC")

    if 'primaryLanguage' in github_repo and github_repo['primaryLanguage'] is not None:
        record['language'] = github_repo['primaryLanguage']['name']

    repo = get_repo(repos, (org, repo_name))
    repo[GITHUB] = record


def get_repo(repos: Repos, key: RepoKey) -> Repo:
    '''Lookup the key in repos, adding if not present, and return the Repo.'''
    if key in repos:
        return repos[key]
    else:
        repo = Repo()
        repos[key] = repo
        return repo


def list_codacy(repos: Repos, codacy_org_data: CodacyOrgData, organization: str):
    '''Pull the organization's Codacy info and add it to repos and codacy_org_data.'''
    headers = {
        'Accept': 'application/json',
        'api-token': CODACY_API_KEY
    }

    codacy_org = f'{CODACY_BASE}/organizations/gh/{organization}'

    logging.info("call codacy join") #TODO REMOVE

    # list people requests for this org in Codacy
    #r = requests.get(f'{CODACY_BASE}/organizations/gh/{organization}/people/suggestions', params={
    res = requests.get(f'{codacy_org}/join', params={
    }, headers = headers, timeout=5)
    logging.info("join response %s", res.text) #TODO REMOVE
    json = res.json()
    join_data = json['data']
    #CodacyOrgData[organization] = {"people_suggestions": data}

    res = requests.get(f'{codacy_org}/people', params={
    }, headers = headers, timeout=5)
    json = res.json()
    people_data = json['data']
    codacy_org_data[organization] = {"people": people_data, "join": join_data}

    # walk repos in Codacy
    res = requests.get(f'{codacy_org}/repositories', params={
    }, headers = headers, timeout=5)

    json = res.json()
    data = json['data']
    for record in data:
        repo_name = record['name']
        if organization != record['owner']:
            logging.error(f"org not owner {organization} {repo_name}")
            continue
        logging.info(f"Codacy {repo_name}")
        codacy_org_repos = f'{CODACY_BASE}/analysis/organizations/gh/{organization}/repositories'
        tools_res = requests.get(
            f'{codacy_org_repos}/{repo_name}/tools',
            params={}, headers = headers, timeout=5)
        tools = tools_res.json()

        # "tools": {
        #     "data": [
        #         {
        #             "isClientSide": false,
        #             "name": "remark-lint",
        #             "settings": {
        #                 "isEnabled": false,
        #                 "usesConfigurationFile": false
        #             }
        #         },

        tools_data = tools["data"]
        tools_client = []
        tools_server = []
        for tool in tools_data:
            tool_name = tool["name"]
            if tool_name in ["Bandit", "Checkov", "PMD", "SpotBugs", "Codacy ScalaMeta Pro"]:
                tools_list = tools_client if tool["isClientSide"] else tools_server
                tools_list.append(tool_name)
        record["tools_full"] = tools
        record["tools_client"] = tools_client
        record["tools_server"] = tools_server
        repo = get_repo(repos, (organization, repo_name))
        repo[CODACY] = record


def list_sonar(repos: Repos, org_key: str):
    '''Pull SonarCloud data for an organization and put it in repos.'''
    logging.info(f"SonarCloud organization {org_key}")

    # TODO fix bug - terra-data-catalog is missing

    url = f"https://sonarcloud.io"\
        "/api/components/search_projects?boostNewProjects=true&ps=50"\
        "&facets=reliability_rating%2Csecurity_rating%2Csqale_rating%2C"\
        "coverage%2Cduplicated_lines_density%2Cncloc%2Calert_status%2C"\
        "languages%2Ctags&f=analysisDate%2CleakPeriodDate&"\
        f"organization={org_key}"

    auth = HTTPBasicAuth(SONARCLOUD_API_KEY, '')
    res = requests.get(url, auth=auth, timeout=5)
    json = res.json()
    if 'components' not in json:
        logging.info(f"SonarCloud - error {org_key}")
        return
    components = json['components']
    for record in components:
        project_key = record['key']
        project_url = "https://sonarcloud.io/api/navigation/component?"\
            f"component={project_key}"
        res = requests.get(project_url, auth=auth, timeout=5)
        project_json = res.json()
        if 'alm' not in project_json:
            logging.error(f"SonarCloud - error no alm in {project_key}")
            continue
        alm = project_json['alm']
        gh_url = alm['url']
        url_parts = gh_url.split('/')
        gh_org = url_parts[-2]
        gh_project = url_parts[-1]
        logging.info(f"SonarCloud - {gh_project}")
        repo = get_repo(repos, (gh_org, gh_project))
        repo[SONAR] = project_json #record


def get_data() -> Repos:
    '''Pull data from SAST tools into Firestore.'''
    repos = Repos()
    codacy_org_data = CodacyOrgData()

    # initialize repos list from existing security controls
    repo_list_from_security_controls(repos)

    # add and merge from codacy
    for org in CODACY_ORGS:
        list_codacy(repos, codacy_org_data, org)

    # add and merge from sonarcloud
    for org_key in SONAR_ORGS.values():
        list_sonar(repos, org_key)

    # query github for metadata on all above repos
    list_github(repos)
    return repos, codacy_org_data


def update_sast_values():
    '''Update security-controls and sast-details in Firestore.'''
    sast_collection = fs.collection(SAST_DETAILS)

    repos, codacy_org_data = get_data()

    repos_for_json = dict()
    for org,rep in repos:
        repos_for_json[f"{org}/{rep}"] = repos[(org, rep)]

    codacy_doc = sast_collection.document('Codacy')
    codacy_doc.set(codacy_org_data, merge=False)
    repos_doc = sast_collection.document('Repos')
    repos_doc.set(repos_for_json, merge=False)
