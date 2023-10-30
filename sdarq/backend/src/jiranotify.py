from jira import JIRA
import logging
import slacknotify
import os

jira_username = os.getenv('jira_username')
jira_api_token = os.getenv('jira_api_token')
jira_instance = os.getenv('jira_instance')
appsec_sdarq_error_channel = os.getenv('appsec_sdarq_error_channel')



global jira
jira = JIRA(basic_auth=(jira_username, jira_api_token),
            options={'server': jira_instance})


def create_task_ticket(appsec_jira_project_key, ticket_summary, ticket_description):
    """
    This function creates a Jira task ticket
    Args: 
        appsec_jira_project_key
        ticket_summary
        ticket_description
    Returns: 
        Jira Ticket id
    """
    try:
        jira_ticket = jira.create_issue(project=appsec_jira_project_key,
                                        summary=ticket_summary,
                                        description=str(
                                            ticket_description),
                                        issuetype={'name': 'Task'})
        return jira_ticket
    except Exception as error:
        logging.warning(error)
        slacknotify.slacknotify_jira_ticket_error(error, appsec_sdarq_error_channel, appsec_jira_project_key)
        return None
    

def create_story_ticket(appsec_jira_project_key, ticket_summary, ticket_description):
    """
    This functions creates a Jira story ticket
    Args: 
        appsec_jira_project_key
        ticket_summary
        ticket_description
    Returns: 
        Jira Ticket id
    """
    try:
        jira_ticket = jira.create_issue(project=appsec_jira_project_key,
                                        summary=ticket_summary,
                                        description=str(
                                            ticket_description),
                                        issuetype={'name': 'Story'})
        return jira_ticket
    except Exception as error:
        logging.warning(error)
        slacknotify.slacknotify_jira_ticket_error(error, appsec_sdarq_error_channel, appsec_jira_project_key)
        return None


def create_board_ticket(appsec_jira_project_key, ticket_summary, ticket_description):
    """
    This fucntion creates a Jira task ticket, if the request is successful return Jira Ticket id,
    if not, tries to create a Jira story ticket.
    """
    task = create_task_ticket(appsec_jira_project_key, ticket_summary, ticket_description)
    if task is not None:
        logging.info("Jira Task created successfully!")
    else:
        logging.info("Jira Task creation failed. Creating a story.")

        story = create_story_ticket(appsec_jira_project_key, ticket_summary, ticket_description)
        
        if story is not None:
            logging.info("Story ticket created successfully!")
        else:
            logging.info("Failed to create a story ticket.")