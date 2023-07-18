import json
import logging
import os

import requests

dojo_host = os.getenv('dojo_host')
dojo_api_key = os.getenv('dojo_api_key')
headers = {
    "content-type": "application/json",
    "Authorization": f"Token {dojo_api_key}",
}


products_endpoint = f"{dojo_host}api/v2/products/"

def dojo_create_or_update(name, description, product_type, user_email):
    data = {
        'name': name,
        'description': description,
        'prod_type': product_type}
    response = requests.get(products_endpoint+"?name_exact="+name, headers=headers)
    if response.json()['count'] > 0:
        product_id = response.json()['results'][0]['id']
        data['description'] = data['description'] + " updated by " + user_email
        logging.info(data)
        res = requests.patch(products_endpoint + str(product_id) + "/", headers=headers, data=data)
        if res.status_code != 200:
            logging.info("failed to update product")
            logging.info(res.text)
        else:
            logging.info("Product updated: %s by %s request",
                        name, user_email)
            logging.info(res.text)
        return product_id
    else:
        res = requests.post(products_endpoint,
                                headers=headers, data=json.dumps(data))
        res.raise_for_status()
        product_id = res.json()['id']

        logging.info("Product created: %s by %s request",
                        name, user_email)
        return product_id