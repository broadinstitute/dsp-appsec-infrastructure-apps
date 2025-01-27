import json
import logging
import os
import slacknotify
import requests

dojo_host = os.getenv('dojo_host')
dojo_api_key = os.getenv('dojo_api_key')
headers = {
    "content-type": "application/json",
    "Authorization": f"Token {dojo_api_key}",
}


products_endpoint = f"{dojo_host}api/v2/products/"

def dojo_create_or_update(name, description, product_type, user_email, appsec_slack_channel, security_champion, dojo_host_url):
    data = {
        'name': name,
        'description': description,
        'prod_type': product_type}
    response = requests.get(products_endpoint+"?name_exact="+name, headers=headers)
    if response.json()['count'] > 0:
        product_id = response.json()['results'][0]['id']
        if not isinstance(product_id, int):
            #this should never happen
            return None
        data['description'] = data['description'] + " updated by " + user_email
        res = requests.patch(products_endpoint + str(product_id) + "/", headers=headers, data=json.dumps(data))
        if res.status_code != 200:
            logging.info("failed to update product")
            return None
        else:
            logging.info("Product updated: %s by %s request",
                        name, user_email)
            
            slacknotify.slacknotify_updateprod_jira(
            appsec_slack_channel,
            name,
            security_champion,
            product_id,
            dojo_host_url)
            
        return product_id
    else:
        res = requests.post(products_endpoint,
                                headers=headers, data=json.dumps(data))
        res.raise_for_status()
        product_id = res.json()['id']

        slacknotify.slacknotify_jira(
        appsec_slack_channel,
        name,
        security_champion,
        product_id,
        dojo_host_url)

        logging.info("Product created: %s by %s request",
                        name, user_email)
        return product_id