import json
from flask import request, make_response
from flask_api import FlaskAPI
from flask_cors import CORS, cross_origin
import defectdojo as wrapper
from slacker import Slacker
from jira import JIRA
import os

# # # Read config
# with open('config.json') as config_file:
#     data = json.load(config_file)

#     dojo_host = data['dojo_host']
#     dojo_user = data['dojo_user']
#     dojo_api_key = data['dojo_api_key']
#     slack_token = data['slack_token']
#     jira_username = data['jira_username']
#     jira_api_token = data['jira_api_token']
#     jira_instance = data['jira_instance']


dojo_host = os.getenv('dojo_host')
dojo_user = os.getenv('dojo_user')
dojo_api_key = os.getenv('dojo_api_key')
slack_token = os.getenv('slack_token')
jira_username = os.getenv('jira_username')
jira_api_token = os.getenv('jira_api_token')
jira_instance = os.getenv('jira_instance')

sdarq_host = os.getenv('sdarq_host')

# Slack communication via slack_token
slack = Slacker(slack_token)

# Instantiate the DefectDojo backend wrapper
dd = wrapper.DefectDojoAPI(dojo_host, dojo_api_key, dojo_user, debug=True)
app = FlaskAPI(__name__)

# Instantiate the Jira backend wrapper
global jira
jira = JIRA(basic_auth=(jira_username, jira_api_token),options={'server': jira_instance })

# Prepare to send to DefectDojo
@app.route('/health/', methods=['GET'])
def health():
    return ''

@app.route('/submit/', methods=['POST'])
@cross_origin(origins=[sdarq_host])
def submit():
    jsonData = request.get_json()
    appName = jsonData['Service']
    securityChamp = jsonData['Security champion']

    # Create a product in DefectDojo
    prod_type = 1
    product = dd.create_product(appName, "Created for testing", prod_type)

    if product.success:
        product_id = product.id()
    else:
        raise Exception("dd.create_product(): " + str(product))

    # Create a Jira ticket if user chooses a Jira project
    if 'JiraProject' in jsonData:
        project_key_id = jsonData['JiraProject']
        jira_description = json.dumps(jsonData['Ticket_Description']).strip('[]')
        one = jira_description.strip('", "').replace('", "',' \n- ')
        jira_ticket = jira.create_issue(project=project_key_id,
                                        summary='New security requirements issue',
                                        description=str(one),
                                        issuetype={'name': 'Task'})
        del jsonData['Ticket_Description']  # delete Ticket_Description from json, so it will not be added to DefectDojo product description
        data = json.dumps(jsonData).strip('{}')
        data1 = data.strip(',').replace(',',' \n')
        data2 = data1.strip('[').replace('[',' ')
        data3 = data2.strip(']').replace(']',' ')
        data4 = data3.strip('""').replace('"', ' ')
         # Set product description
        productDescription = dd.set_product(product_id, description=data4)
         # Set Slack notification
        slack.chat.post_message('#dsp-security',
                                '*New service engagement created* :notebook_with_decorative_cover: \n 1. Project name: `' + appName + '`\n 2. DefectDojo URL:`' + dojo_host + 'product/' + str(
                                  product_id) + '`\n 3. Jira Issue Url: `' + jira_instance + '/projects/' + str(project_key_id) + "/issues/"+ str(jira_ticket) + "` \n 4. Security champion: `" + securityChamp + "`")
        slack.chat.post_message('#dsde-qa',
                                '*New service engagement created* :notebook_with_decorative_cover: \n 1. Project name: `' + appName + '`\n 2. DefectDojo URL:`' + dojo_host + 'product/' + str(
                                product_id) + '`\n 3. Jira Issue Url: `' + jira_instance + '/projects/' + str(project_key_id) + "/issues/"+ str(jira_ticket) + "` \n 4. Security champion: `" + securityChamp + "`")
    else:
        # Set Slack notification
        slack.chat.post_message('#dsp-security',
                                '*New service engagement created* :notebook_with_decorative_cover: \n 1. Project name: `' + appName + '`\n 2. DefectDojo URL:`' + dojo_host + 'product/' + str(
                                  product_id) + "` \n 3. Security champion: `" + securityChamp + "`")
        slack.chat.post_message('#dsde-qa',
                                 '*New service engagement created* :notebook_with_decorative_cover: \n 1. Project name: `' + appName + '`\n 2. DefectDojo URL:`' + dojo_host + 'product/' + str(
                                product_id) + "` \n 3. Security champion: `" + securityChamp + "`")
        data = json.dumps(jsonData).strip('{}')
        data1 = data.strip(',').replace(',',' \n')
        data2 = data1.strip('[').replace('[',' ')
        data3 = data2.strip(']').replace(']',' ')
        data4 = data3.strip('""').replace('"', ' ')
         # Set product description
        productDescription = dd.set_product(product_id, description=data4)

    response = make_response((json.dumps(data),200,
                       {"X-Frame-Options": "SAMEORIGIN",
                        "X-XSS-Protection":"1; mode=block",
                        "X-Content-type-Options":"nosniff"}))


    return response


if __name__== "__main__":
     app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

