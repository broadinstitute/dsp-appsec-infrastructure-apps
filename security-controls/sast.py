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
CODACY_API_KEY=os.getenv("CODACY_API_KEY").strip()
SONARCLOUD_API_KEY=os.getenv("SONARCLOUD_API_KEY").strip()
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN").strip()

CODACY_HEADERS = {
    'Accept': 'application/json',
    'api-token': CODACY_API_KEY
}

def codacy_org(organization: str) -> str:
    '''path for codacy org'''
    return f'{CODACY_BASE}/organizations/gh/{organization}'


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

def get_if(obj: dict, key: str) -> str:
    '''return obj[value] or empty string if missing'''
    value = obj.get(key)
    if value is None:
        value = ""
    return value

def repo_list_from_security_controls(repos: Repos):
    """Initalize repos from Firestore."""
    sc_collection = fs.collection(SECURITY_CONTROLS)
    sc_docs = sc_collection.stream()
    for doc in sc_docs:
        project = doc.to_dict()
        repo_url = get_if(project,'github')
        logging.info("github %s sast %s link %s",
            repo_url, get_if(project,'sast'), get_if(project,'sast_link'))
        match = repo_re.match(repo_url)
        if match is None:
            logging.warning('SAST controls ignoring %s github="%s"', doc.id, repo_url)
            continue
        else:
            org = match.group(1)
            repo_name = match.group(2)
            if org.lower() == 'databiosphere':
                org = 'DataBiosphere'
            if org.lower() == 'broadinstitute':
                org = 'broadinstitute'
            get_repo(repos, (org, repo_name))

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

    logging.info("GitHub %s %s", repo_name, org)
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

    logging.info('SAST will update %s/%s', org, repo_name)
    repo = get_repo(repos, (org, repo_name))
    repo[GITHUB] = record

def get_repo(repos: Repos, key: RepoKey) -> Repo:
    '''Lookup the key in repos, adding if not present, and return the Repo.'''
    if key in repos:
        repo = repos[key]
    else:
        repo = Repo()
        repos[key] = repo
    return repo

def codacy_get(path):
    '''call Codacy REST GET and return json response data'''
    logging.info("codacy get %s", path)
    res = requests.get(path, params={}, headers=CODACY_HEADERS, timeout=5)
    logging.info("response %s", res.text)
    if res.status_code != 200:
        logging.error("codacy error %s %s %s", path, res.status_code, res.text)
        return None
    json = res.json()
    return json['data']

def list_codacy_org_data(codacy_org_data: CodacyOrgData, organization: str):
    '''get codacy metadata on organization'''

    # list people requests for this org in Codacy
    join_data = codacy_get(f'{codacy_org(organization)}/join')
    people_data = codacy_get(f'{codacy_org(organization)}/people')
    codacy_org_data[organization] = {"people": people_data, "join": join_data}

def list_codacy_repos(repos: Repos, organization: str):
    '''get codacy metadata on github repos'''
    # walk repos in Codacy
    codacy_repos = codacy_get(f'{codacy_org(organization)}/repositories')
    for record in codacy_repos:
        repo_name = record['name']
        if organization != record['owner']:
            logging.error("org not owner %s %s", organization, repo_name)
            continue
        logging.info("Codacy %s", repo_name)
        codacy_org_repos = f'{CODACY_BASE}/analysis/organizations/gh/{organization}/repositories'
        tools_data = codacy_get(f'{codacy_org_repos}/{repo_name}/tools')
        tools_client = []
        tools_server = []
        for tool in tools_data:
            tool_name = tool.get("name")
            if tool_name in ["Bandit", "Checkov", "PMD", "SpotBugs", "Codacy ScalaMeta Pro"]:
                tools_list = tools_client if tool["isClientSide"] else tools_server
                tools_list.append(tool_name)
        record["tools_full"] = tools_data
        record["tools_client"] = tools_client
        record["tools_server"] = tools_server
        repo = get_repo(repos, (organization, repo_name))
        repo[CODACY] = record

def list_codacy(repos: Repos, codacy_org_data: CodacyOrgData, organization: str):
    '''Pull the organization's Codacy info and add it to repos and codacy_org_data.'''

    list_codacy_org_data(codacy_org_data, organization)
    list_codacy_repos(repos, organization)


def list_sonar(repos: Repos, org_key: str):
    '''Pull SonarCloud data for an organization and put it in repos.'''
    logging.info("SonarCloud organization %s", org_key)

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
        logging.info("SonarCloud - error %s", org_key)
        return
    components = json['components']
    for record in components:
        project_key = record['key']
        res = requests.get("https://sonarcloud.io/api/navigation/component?"\
            f"component={project_key}", auth=auth, timeout=5)
        project_json = res.json()
        if 'alm' not in project_json:
            logging.error("SonarCloud - error no alm in %s", project_key)
            continue
        gh_url = project_json['alm']['url']
        url_parts = gh_url.split('/')
        gh_org = url_parts[-2]
        gh_project = url_parts[-1]
        logging.info("SonarCloud - repo %s", gh_project)
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

    logging.info("update_sast_values")

    logging.info("lengths %s %s %s",
        len(CODACY_API_KEY),
        len(SONARCLOUD_API_KEY),
        len(GITHUB_TOKEN))

    sast_collection = fs.collection(SAST_DETAILS)

    repos, codacy_org_data = get_data()

    repos_for_json = {}
    for org,rep in repos:
        repos_for_json[f"{org}/{rep}"] = repos[(org, rep)]

    codacy_doc = sast_collection.document('Codacy')
    codacy_doc.set(codacy_org_data, merge=False)
    repos_doc = sast_collection.document('Repos')
    repos_doc.set(repos_for_json, merge=False)
