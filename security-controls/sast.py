"""Update SAST security-controls data."""

import logging
import os
import re

import requests
from google.cloud import firestore
from requests.auth import HTTPBasicAuth

SECURITY_CONTROLS = os.environ['SC_FIRESTORE_COLLECTION']
SAST_DETAILS = os.environ['SAST_FIRESTORE_COLLECTION']

SC_PREVIOUS = "security-controls-previous"
ID = "id"
SAST = "sast"
SAST_LINK = "sast_link"

fs = firestore.Client()

CODACY_BASE = "https://app.codacy.com/api/v3"
CODACY_API_KEY=os.getenv("CODACY_API_KEY").strip()
CODACY_URL = "https://app.codacy.com/gh/{org}/{repo}/dashboard"

SONARCLOUD_BASE = "https://sonarcloud.io/api"
SONARCLOUD_API_KEY=os.getenv("SONARCLOUD_API_KEY").strip()
SONARCLOUD_URL = "https://sonarcloud.io/project/overview?id={project_key}"

GITHUB_GQL_ENDPOINT = "https://api.github.com/graphql"
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN").strip()

CODACY_HEADERS = {
    'Accept': 'application/json',
    'api-token': CODACY_API_KEY
}

def codacy_org(organization: str) -> str:
    '''path for codacy org'''
    return f'{CODACY_BASE}/organizations/gh/{organization}'


repo_re = re.compile(r'https://(www.)?github.com/([a-zA-Z0-9\-_]+)/([a-zA-Z0-9\-_]+)')
RE_GROUP_ORG = 2
RE_GROUP_REPO = 3

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
        sc_record = doc.to_dict()
        repo_url = get_if(sc_record,'github')
        match = repo_re.match(repo_url)
        if match is None:
            logging.warning('SAST controls ignoring %s github="%s"', doc.id, repo_url)
            continue
        org = match.group(RE_GROUP_ORG)
        repo_name = match.group(RE_GROUP_REPO)
        if org.lower() == 'databiosphere':
            org = 'DataBiosphere'
        if org.lower() == 'broadinstitute':
            org = 'broadinstitute'
        repo = get_repo(repos, (org, repo_name))
        sc_record[ID] = doc.id
        repo[SC_PREVIOUS] = sc_record
        logging.debug('SAST controls to be updated for %s github="%s"', doc.id, repo_url)


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

    logging.debug("GitHub %s %s", repo_name, org)
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
    if 'data' not in github or 'repository' not in github['data']:
        logging.error("Cannot access GitHub repo %s %s", org, repo_name)
        return

    github_repo = github['data']['repository']
    if github_repo is None:
        logging.error("Cannot read GitHub repo %s %s", org, repo_name)
        return
    record = {}
    record['private'] = (github_repo['visibility'] != "PUBLIC")

    if 'primaryLanguage' in github_repo and github_repo['primaryLanguage'] is not None:
        record['language'] = github_repo['primaryLanguage']['name']

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
    res = requests.get(path, params={}, headers=CODACY_HEADERS, timeout=5)
    if res.status_code != 200:
        logging.error("codacy error %s %s %s", path, res.status_code, res.text)
        return None
    json = res.json()
    data = json['data']
    return data

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
        logging.debug("Codacy %s %s", organization, repo_name)
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
        repo[SAST_LINK] = CODACY_URL.format(org=organization,repo=repo_name)
        repo[CODACY] = record

def list_codacy(repos: Repos, codacy_org_data: CodacyOrgData, organization: str):
    '''Pull the organization's Codacy info and add it to repos and codacy_org_data.'''

    list_codacy_org_data(codacy_org_data, organization)
    list_codacy_repos(repos, organization)


def list_sonar(repos: Repos, org_key: str):
    '''Pull SonarCloud data for an organization and put it in repos.'''
    logging.debug("SonarCloud organization %s", org_key)

    url = f"{SONARCLOUD_BASE}/components/search_projects?boostNewProjects=true&ps=50"\
        "&facets=reliability_rating%2Csecurity_rating%2Csqale_rating%2C"\
        "coverage%2Cduplicated_lines_density%2Cncloc%2Calert_status%2C"\
        "languages%2Ctags&f=analysisDate%2CleakPeriodDate&"\
        f"organization={org_key}"

    auth = HTTPBasicAuth(SONARCLOUD_API_KEY, '')
    res = requests.get(url, auth=auth, timeout=5)
    json = res.json()
    if 'components' not in json:
        logging.error("SonarCloud - error %s", org_key)
        return
    components = json['components']
    for record in components:
        project_key = record['key']
        res = requests.get(f"{SONARCLOUD_BASE}/navigation/component?"\
            f"component={project_key}", auth=auth, timeout=5)
        project_json = res.json()
        if 'alm' not in project_json:
            logging.error("SonarCloud - error no alm in %s", project_key)
            continue
        gh_url = project_json['alm']['url']
        url_parts = gh_url.split('/')
        gh_org = url_parts[-2]
        gh_project = url_parts[-1]
        logging.debug("SonarCloud - repo %s", gh_project)
        repo = get_repo(repos, (gh_org, gh_project))
        repo[SAST_LINK] = SONARCLOUD_URL.format(project_key=project_key)
        repo[SONAR] = project_json #record


def get_data() -> Repos:
    '''Pull data from SAST tools into Firestore.'''
    repos = Repos()
    codacy_org_data = CodacyOrgData()

    # initialize repos list from existing security controls
    repo_list_from_security_controls(repos)

    # add codacy
    for org in CODACY_ORGS:
        list_codacy(repos, codacy_org_data, org)

    # add sonarcloud
    for org_key in SONAR_ORGS.values():
        list_sonar(repos, org_key)

    # query github for metadata on all above repos
    list_github(repos)
    return repos

def update_sast_values():
    '''Update security-controls and sast-details in Firestore.'''

    try:
        logging.info("update_sast_values")

        logging.debug("lengths %s %s %s",
            len(CODACY_API_KEY),
            len(SONARCLOUD_API_KEY),
            len(GITHUB_TOKEN))

        sast_collection = fs.collection(SAST_DETAILS)
        sc_collection = fs.collection(SECURITY_CONTROLS)

        repos = get_data()

        # store repos data
        for org_name, repo_name in repos:
            repo = repos[(org_name, repo_name)]

            # write unconditionally to sast-details
            repos_doc = sast_collection.document(f"gh-{org_name}-{repo_name}")
            repos_doc.set(repo, merge=False)

            # update sast properties in security-controls only if already there
            sc_previous = repo.get(SC_PREVIOUS)
            if sc_previous:
                sc_doc = sc_collection.document(sc_previous[ID])
                sast_link = repo.get(SAST_LINK)
                if sast_link:
                    logging.info("Setting SAST true on %s", sc_previous[ID])
                    sc_doc.update({SAST:True, SAST_LINK:sast_link})
                else:
                    logging.info("Setting SAST false on %s", sc_previous[ID])
                    sc_doc.update({SAST:False, SAST_LINK:firestore.DELETE_FIELD})

    # pylint: disable=W0703
    except Exception as ex:
        # log but don't terminate process with error status
        logging.exception(ex)
