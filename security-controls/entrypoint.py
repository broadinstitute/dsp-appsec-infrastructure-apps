#!/usr/bin/env python3
"""
This module
- will get all products that have srlc tag and update security controls column for all services/apps
"""

import json
import logging
import os
import re
import requests


def getDDprojects(defect_dojo_key: str, defect_dojo: str, security_controls_firestore_collection: str):
    '''
    Get all DefectDojo projects with srcclr tag
    Update all services 3rd party dependencies scan in security controls with the result link to DD
    '''
    db = firestore.Client()
    products_endpoint = "https://defectdojo.dsp-appsec-dev.broadinstitute.org/api/v2/products/?tag=srcclr"

    headers = {
        "content-type": "application/json",
        "Authorization": f"Token {defect_dojo_key}",
    }

    res = requests.get(products_endpoint,
                       headers=headers, verify=True)

    for product in res.json()['results']:
        setSecConDDlink = db.collection(
            security_controls_firestore_collection).document(product['name'].lower())
        doc = setSecConDDlink.get()
        if bool(doc.to_dict()) is True:
            setSecConDDlink.set({
                u'sourceclear': True,
                u'sourceclear_link': '{0}/product/{1}/finding/open?test_import_finding_action__test_import=&title=&component_name=&component_version=&date=&last_reviewed=&last_status_update=&mitigated=&reporter=17&test__engagement__version=&test__version=&status=&active=unknown&verified=unknown&duplicate=&is_mitigated=&out_of_scope=unknown&false_p=unknown&risk_accepted=unknown&has_component=unknown&has_notes=unknown&file_path=&unique_id_from_tool=&vuln_id_from_tool=&service=&param=&payload=&risk_acceptance=&has_finding_group=unknown&tags=&test__tags=&test__engagement__tags=&test__engagement__product__tags=&tag=&not_tags=&not_test__tags=&not_test__engagement__tags=&not_test__engagement__product__tags=&not_tag=&vulnerability_id=&planned_remediation_date=&endpoints__host=&o='.format(defect_dojo, str(product['id']))
            }, merge=True)


def main():
    defect_dojo_key = os.getenv("DEFECT_DOJO_KEY")
    defect_dojo = os.getenv("DEFECT_DOJO_URL")
    security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']

    getDDprojects(defect_dojo_key, defect_dojo, security_controls_firestore_collection)


if __name__ == "__main__":
    main()
