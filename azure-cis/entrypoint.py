#!/usr/bin/env python3
"""
This module
- initially will get all findings from CIS Azure 
- send Slack notifications with all highs
"""

import requests
import json


# Function to get access token
def get_access_token(client_id, client_secret, resource, token_url):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': resource
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

# Function to get CIS Benchmark data
def get_cis_benchmark_data(subscription_id, access_token):
    url = f'https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Security/assessments?api-version=2021-01-01'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    subscription_id = 'your_subscription_id'
    TENANT_ID = 'your_tenant_id'
    client_id = 'your_client_id'
    client_secret = 'your_client_secret'
    resource = 'https://management.azure.com/'
    token_url = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/token'
    
    # Get access token
    access_token = get_access_token(client_id, client_secret, resource, token_url)
    
    # Fetch CIS Benchmark data
    cis_data = get_cis_benchmark_data(subscription_id, access_token)
    
    # Print or process the data as needed
    print(json.dumps(cis_data, indent=2))

if __name__ == '__main__':
    main()
