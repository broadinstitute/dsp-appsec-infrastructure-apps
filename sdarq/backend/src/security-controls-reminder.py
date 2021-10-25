#!/usr/bin/env python3
"""
This module
- get all security controls for each service
- send notifications/reminder to Appsec team for missing security controls
"""

from google.cloud import firestore
import os
import slacknotify

def get_sec_controls():
    """
    Get all data from Firestore
    Args: None
    Returns: Json data
    """
    
    db = firestore.Client()
    data = []
    docs = db.collection('security-controls').stream()
    for doc in docs:
        data.append(doc.to_dict())
    

def main():
    """
    Implements the security-controls-reminder.py test
    """

security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']

if __name__ == "__main__":
    main()