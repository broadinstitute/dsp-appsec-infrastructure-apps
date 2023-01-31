#!/usr/bin/env python3
"""
This module
- will get all products that have srlc & zap tag and update security controls column for all services/apps
"""
import logging
import os

import google.cloud.logging
import requests
from google.cloud import firestore
from sast import update_sast_values


def update_dependecies_scan_values(defect_dojo_key: str, defect_dojo: str, security_controls_firestore_collection: str, dep_scan_link: str, defect_dojo_host: str):
    '''
    Get all DefectDojo projects with srcclr tag
    Update all services 3rd party dependencies scan in security controls with the result link to DD
    '''
    firestore_docs = firestore.Client()
    products_endpoint = f"{defect_dojo}/api/v2/products/?tag=srcclr&limit=1000"

    headers = {
        "content-type": "application/json",
        "Authorization": f"Token {str(defect_dojo_key)}",
    }

    res = requests.get(products_endpoint,
                       headers=headers, verify=True, timeout=15)

    for product in res.json()['results']:
        doc_ref = firestore_docs.collection(
            security_controls_firestore_collection).document(product['name'].lower())
        doc = doc_ref.get()
        if bool(doc.to_dict()) is True:
            logging.info(
                "Third party dependecies scan value and link updated for %s ", product['name'])
            doc_ref.set({
                'sourceclear': True,
                'sourceclear_link': f'{defect_dojo_host}/product/{str(product["id"])}/finding/{dep_scan_link}'
            }, merge=True)


def update_dast_values(defect_dojo_key: str, defect_dojo: str, security_controls_firestore_collection: str, dast_link: str, defect_dojo_host: str):
    '''
    Get all DefectDojo projects with zap tag
    Update all services DAST value in security controls with the result link to DD
    '''
    firestore_docs = firestore.Client()
    products_endpoint = f"{defect_dojo}/api/v2/products/?tag=zap&limit=1000"

    headers = {
        "content-type": "application/json",
        "Authorization": f"Token {str(defect_dojo_key)}",
    }

    res = requests.get(products_endpoint,
                       headers=headers, verify=True, timeout=15)
    for product in res.json()['results']:
        doc_ref = firestore_docs.collection(
            security_controls_firestore_collection).document(product['name'].lower())
        doc = doc_ref.get()
        if bool(doc.to_dict()) is True:
            logging.info("DAST value and link updated for %s ",
                         product['name'])
            doc_ref.set({
                'zap': True,
                'vulnerability_management': f'{defect_dojo_host}/product/{str(product["id"])}/finding/{dast_link}'
            }, merge=True)


def main():
    """
    Implements the entrypoint.
    """

    # configure logging
    client = google.cloud.logging.Client()
    client.setup_logging()

    defect_dojo_key = os.getenv("DEFECT_DOJO_KEY")
    defect_dojo = os.getenv("DEFECT_DOJO_URL")
    defect_dojo_host = os.getenv("DEFECT_DOJO")
    security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']
    dep_scan_link = os.getenv("DEP_SCAN_LINK")
    dast_link = os.getenv("DAST_LINK")


    update_dependecies_scan_values(
        defect_dojo_key, defect_dojo, security_controls_firestore_collection, dep_scan_link, defect_dojo_host)

    update_dast_values(defect_dojo_key, defect_dojo,
                       security_controls_firestore_collection, dast_link, defect_dojo_host)

    update_sast_values()


if __name__ == "__main__":
    main()
