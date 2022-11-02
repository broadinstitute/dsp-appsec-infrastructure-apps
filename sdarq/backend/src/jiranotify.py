from jira import JIRA
import os

jira_username = os.getenv('jira_username')
jira_api_token = os.getenv('jira_api_token')
jira_instance = os.getenv('jira_instance')


global jira
jira = JIRA(basic_auth=(jira_username, jira_api_token),
            options={'server': jira_instance})


def create_board_ticket(appsec_jira_project_key, ticket_summary, ticket_description):
    jira_ticket = jira.create_issue(project=appsec_jira_project_key,
                                    summary=ticket_summary,
                                    description=str(
                                        ticket_description),
                                    issuetype={'name': 'Task'})
    return jira_ticket