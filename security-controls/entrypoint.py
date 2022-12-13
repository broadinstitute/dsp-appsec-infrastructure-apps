#!/usr/bin/env python3
"""
This module
- will get all products that have srlc & zap tag and update security controls column for all services/apps
"""
import os, logging
import requests
from google.cloud import firestore



def update_dependecies_scan_values(defect_dojo_key: str, defect_dojo: str, security_controls_firestore_collection: str, dep_scan_link: str):
    '''
    Get all DefectDojo projects with srcclr tag
    Update all services 3rd party dependencies scan in security controls with the result link to DD
    '''
    db = firestore.Client()
    products_endpoint = "{0}/api/v2/products/?tag=srcclr".format(defect_dojo)

    headers = {
        "content-type": "application/json",
        "Authorization": "Token {0}".format(str(defect_dojo_key)),
    }

    res = requests.get(products_endpoint,
                       headers=headers, verify=True)

    for product in res.json()['results']:
        doc_ref = db.collection(
            security_controls_firestore_collection).document(product['name'].lower())
        doc = doc_ref.get()
        if bool(doc.to_dict()) is True:
            logging.info("Third party dependecies scan value and link updated for %s ", product['name'])
            doc_ref.set({
                u'sourceclear': True,
                u'sourceclear_link': '{0}/product/{1}/finding/{2}'.format(defect_dojo, str(product['id']), dep_scan_link)
            }, merge=True)


def update_dast_values(defect_dojo_key: str, defect_dojo: str, security_controls_firestore_collection: str, dast_link: str):
    '''
    Get all DefectDojo projects with zap tag
    Update all services DAST value in security controls with the result link to DD
    '''
    db = firestore.Client()
    products_endpoint = "{0}/api/v2/products/?tag=zap".format(defect_dojo)

    headers = {
        "content-type": "application/json",
        "Authorization": "Token {0}".format(str(defect_dojo_key)),
    }

    res = requests.get(products_endpoint,
                       headers=headers, verify=True)
    for product in res.json()['results']:
        doc_ref = db.collection(
            security_controls_firestore_collection).document(product['name'].lower())
        doc = doc_ref.get()
        if bool(doc.to_dict()) is True:
            logging.info("DAST value and link updated for %s ", product['name'])
            doc_ref.set({
                u'zap': True,
                u'vulnerability_management': '{0}/product/{1}/finding/{2}'.format(defect_dojo, str(product['id']))
            }, merge=True)



def main():
    """
    Implements the entrypoint.
    """
    defect_dojo_key = os.getenv("DEFECT_DOJO_KEY")
    defect_dojo = os.getenv("DEFECT_DOJO_URL")
    security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']
    dep_scan_link = os.getenv("DEP_SCAN_LINK")
    dast_link = os.getenv("dast_link")

    # configure logging
    logging.basicConfig(level=logging.INFO)

    update_dependecies_scan_values(defect_dojo_key, defect_dojo, security_controls_firestore_collection, dep_scan_link)

    update_dast_values(defect_dojo_key, defect_dojo, security_controls_firestore_collection, dast_link)


if __name__ == "__main__":
    main()
