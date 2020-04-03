from jira import JIRA
from pprint import pprint
import json
import re


def get_jira_details():
  """
  Get Jira details
  Instance: https://broadworkbench.atlassian.net/secure/BrowseProjects.jspa
  """
  with open('config.json') as config_file:
    res = json.load(config_file)

  return {
    "jira_username": res['jira_username'],
    "jira_api_token": res['jira_api_token'],
    "jira_instance": res['jira_instance']
  }

global jira

def auth():
  """
  Authenticate to broadworkbench.atlassian.net Jira Cloud Instance
  """
  global jira
  jd = get_jira_details()
  jira = JIRA(
    basic_auth=(jd['jira_username'], jd['jira_api_token']),
    options={
      'server': jd['jira_instance']
    }
  )

def get_all_projects():
  """
  Return a list of all projects
  """
  projects = jira.projects()
  return projects, type(projects)

def get_single_project_details(project_name):
  """
  Get single project info given a project_id
  Example project name: 'Cloud Integrations'
  """
  project = jira.project(project_name)
  name = project.name
  return name

def get_regular_issue(issue_id):
  """
  Get a single issue in a particular project
  Example issue: 'AAA-6666'
  """
  issue = jira.issue(issue_id)
  return issue

def get_security_issue(issue_id, fields='summary, content, security, sourceclear, codacy'):
  """
  Get a security specific issue
  Example issue: 'AAA-6666'
  """
  compliance_issue = jira.issue(issue_id)
  return compliance_issue

def create_single_security_issue(project_key_id):
  """
  Create a security issue automatically
  Example: "Use Vault to store secrets"
  """
  new_issue = jira.create_issue(project=project_key_id,
                                summary='New security requirements issue',
                                description='Description of new security requirements issue',
                                issuetype={'name': 'Task'})
  # new_issue = jira.create_issue(fields=new_issue)
  print("+ Single Security JIRA issue created: {}".format(new_issue))
  return new_issue

def create_multiple_security_issues(project_key_id):
  """
  Create multiple security issues automatically
  Example:  - Use Vault to store secrets
            - Has pentesting been done
            - Is unit testing part of your workflow
  """
  issue_list = [
    {
      'project': {'key': project_key_id},
      'summary': 'First issue of many',
      'description': 'Look into this one',
      'issuetype': {'name': 'Bug'},
    },
    {
      'project': {'key': project_key_id},
      'summary': 'Second issue',
      'description': 'Another one',
      'issuetype': {'name': 'Bug'},
    },
    {
      'project': {'key': project_key_id},
      'summary': 'Last issue',
      'description': 'Final issue of batch.',
      'issuetype': {'name': 'Bug'},
    }]

  new_multiple_issues = jira.create_issues(field_list=issue_list)
  print("+ New multiple Security issues created: {}".format(new_multiple_issues))
  return new_multiple_issues

def get_compliance_issue(issue_id, fields='clia, comment, fisma, your_favorite_compliance_framework_here'):
    """
    Get a compliance specific issue
    Example issue: 'AAA-6666'
    """
    compliance_issue = jira.issue(issue_id)
    return compliance_issue

def main():
  auth()

  # all_projects   = get_all_projects()
  # print("All projects   :", all_projects)

  # single_project = get_single_project_details('ATP')
  # print("Single Project :", all_projects)

  # single_issue   = get_regular_issue("ATP-1")
  # print("Single Issue   :", single_issue)

  # new_security_issue = create_single_security_issue('ATP')
  # pprint(new_security_issue)

  # new_multiple_issues = create_multiple_security_issues('ATP')
  # print(new_multiple_issues)

  # print("All projects:", all_projects)


if __name__ == "__main__":
  main()
