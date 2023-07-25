from jira import JIRA
import logging
import os

jira_username = os.getenv('jira_username')
jira_api_token = os.getenv('jira_api_token')
jira_instance = os.getenv('jira_instance')


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
        Jira Ticket id or None (with an exception)
    """
    try:
        jira_ticket = jira.create_issue(project=appsec_jira_project_key,
                                        summary=ticket_summary,
                                        description=str(
                                            ticket_description),
                                        issuetype={'name': 'Task'})
        return jira_ticket
    except Exception as error:
        print(f"Jira Task creation failed with error: {error}")
        logging.warning(error)
        return None
    

def create_story_ticket(appsec_jira_project_key, ticket_summary, ticket_description):
    """
    This functions creates a Jira story ticket
    Args: 
        appsec_jira_project_key
        ticket_summary
        ticket_description
    Returns: 
        Jira Ticket id or None (with an exception)
    """
    try:
        jira_ticket = jira.create_issue(project=appsec_jira_project_key,
                                        summary=ticket_summary,
                                        description=str(
                                            ticket_description),
                                        issuetype={'name': 'Story'})
        return jira_ticket
    except Exception as error:
        print(f"Jira Story creation failed with error: {error}")
        logging.warning(error)
        return None


def create_board_ticket(appsec_jira_project_key, ticket_summary, ticket_description):
    """
    This fucntion creates a Jira task ticket, if the request is successful return Jira Ticket id,
    if not, tries to create a Jira story ticket.
    """
    task = create_task_ticket(appsec_jira_project_key, ticket_summary, ticket_description)
    if task is not None:
        print("Jira Task created successfully!")
        logging.info("Jira Task created successfully!")
    else:
        print("Jira Task creation failed. Creating a story.")
        logging.info("Jira Task creation failed. Creating a story.")

        story = create_story_ticket(appsec_jira_project_key, ticket_summary, ticket_description)
        
        if story is not None:
            print("Story ticket created successfully!")
            logging.info("Story ticket created successfully!")
        else:
            print("Failed to create a story ticket.")
            logging.info("Failed to create a story ticket.")