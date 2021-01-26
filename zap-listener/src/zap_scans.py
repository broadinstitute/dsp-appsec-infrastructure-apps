#!/usr/bin/env python3
# The modules includes
# - method to fetch an access token (for running scans as a authenticated user)
# - individual "steps" of each zap scans
# - "complete" scans that include different steps depending on the type of scan
# - a "compliance scan" method that takes a project, url, and scan type, and returns a filename
import time, os
from pprint import pprint
from zapv2 import ZAPv2
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
import json

def get_gc_token():
    SA_KEY = os.getenv('ZAP_AUTH_SECRET')
    key_json = json.loads(SA_KEY)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        key_json, scopes=[
            'profile', 'email', 'openid',
            'https://www.googleapis.com/auth/cloud-billing',
        ],
    )
    credentials.refresh(Http())
    return credentials.access_token

def zap_init(project):
    # Connect to ZAP
    owasp_key - '12345'
    zap = ZAPv2(apikey=owasp_key, proxies={'http': 'http://127.0.0.1:8008', 'https': 'http://127.0.0.1:8008'})
    # Use the line below if ZAP is not listening on port 8080, for example, if listening on port 8090
    
    zap.context.new_context(project, owasp_key)
    return zap

def zap_auth(zap):
    print("Authenticating via Replacer...")
    token = get_gc_token()
    bearer = "Bearer {}".format(token)
    zap.replacer.add_rule(description="auth", enabled=True, matchtype="REQ_HEADER", matchregex=False, matchstring="Authorization", replacement=bearer)
    return zap

def zap_access(zap, target):
    # Proxy a request to the target so that ZAP has something to deal with
    print('Accessing target {}'.format(target))
    zap.urlopen(target)
    # Give the sites tree a chance to get updated
    time.sleep(2)
    return zap

def zap_spider(zap, target):
    print('Spidering target {}'.format(target))
    scanid = zap.spider.scan(target)
    # Give the Spider a chance to start
    time.sleep(2)
    while (int(zap.spider.status(scanid)) < 100):
        # Loop until the spider has finished
        print('Spider progress %: {}'.format(zap.spider.status(scanid)))
        time.sleep(2)

    print ('Spider completed')
    return zap

def zap_auth_spider(zap, target):

    zap = zap_auth(zap)

    print('Spidering target {}'.format(target))
    scanid = zap.spider.scan(target)
    # Give the Spider a chance to start
    time.sleep(2)
    count = 2
    while (int(zap.spider.status(scanid)) < 100):
        # Loop until the spider has finished
        print('Spider progress %: {}'.format(zap.spider.status(scanid)))
        time.sleep(2)
        count += 2
        if count > 1800:
            zap = zap_auth(zap)
            count = 0

    print ('Spider completed')
    return zap

def zap_auth_ajax_spider(zap, target)
    print('Ajax Spider target {}'.format(target))
    zap = zap_auth(zap)
    scanID = zap.ajaxSpider.scan(target)
    timeout = time.time() + 60*10   # 2 minutes from now
    # Loop until the ajax spider has finished or the timeout has exceeded
    while zap.ajaxSpider.status == 'running':
        if time.time() > timeout:
            break
        print('Ajax Spider status' + zap.ajaxSpider.status)
        time.sleep(2)

    print('Ajax Spider completed')
    return zap

def zap_passive(zap):
    while (int(zap.pscan.records_to_scan) > 0):
        print ('Records to passive scan : {}'.format(zap.pscan.records_to_scan))
        time.sleep(2)

    print ('Passive Scan completed')
    return zap

def zap_auth_active(zap, target):
    zap = zap_auth(zap)

    print ('Active Scanning target {}'.format(target))
    scanid = zap.ascan.scan(target)
    count = 0
    while (int(zap.ascan.status(scanid)) < 100):
        # Loop until the scanner has finished
        print ('Scan progress %: {}'.format(zap.ascan.status(scanid)))
        time.sleep(5)
        count += 5
        if count > 1800:
            zap = zap_auth(zap)
            count = 0

    print ('Active Scan completed')

    return zap

def zap_active(zap, target):
    print ('Active Scanning target {}'.format(target))
    scanid = zap.ascan.scan(target)
    while (int(zap.ascan.status(scanid)) < 100):
        # Loop until the scanner has finished
        print ('Scan progress %: {}'.format(zap.ascan.status(scanid)))
        time.sleep(5)

    print ('Active Scan completed')

    return zap    

def zap_write(zap, fn):
    with open(fn, 'wb') as f:
        f.write(zap.core.xmlreport().encode('utf-8'))

def zap_baseline(project, target):

    zap = zap_init(project)
    zap = zap_access(zap, target)
    zap = zap_spider(zap, target)
    zap = zap_passive(zap)

    fn = '{}_zap_report.xml'.format(project)
    zap_write(zap, fn)

    return fn

def zap_auth(project, target):

    zap = zap_init(project)
    zap = zap_access(zap, target)
    zap = zap_auth_spider(zap, target)
    zap = zap_passive(zap)

    fn = '{}_auth_zap_report.xml'.format(project)
    zap_write(zap, fn)

    return fn    

def zap_auth(project, target):

    zap = zap_init(project)
    zap = zap_access(zap, target)
    zap = zap_auth_spider(zap, target)
    zap = zap_passive(zap)
    zap = zap_auth_active(zap, target)

    fn = '{}_auth_zap_report.xml'.format(project)
    zap_write(zap, fn)

    return fn    

def zap_auth(project, target):

    zap = zap_init(project)
    zap = zap_access(zap, target)
    zap = zap_auth_spider(zap, target)
    zap = zap_passive(zap)
    zap = zap_auth_active(zap, target)

    fn = '{}_auth_zap_report.xml'.format(project)
    zap_write(zap, fn)

    return fn    

def zap_api(project, target):

    zap = zap_init(project)
    zap = zap_access(zap, target)
    token = get_gc_token()
    zap.openapi.import_url(url=target, hostoverride=None, apikey=token)
    zap = zap_auth_spider(zap, target)
    zap = zap_passive(zap)
    zap = zap_auth_active(zap, target)

    fn = '{}_api_zap_report.xml'.format(project)
    zap_write(zap, fn)

    return fn

def zap_ui(project, target):

    zap = zap_init(project)
    zap = zap_access(zap, target)
    zap = zap_auth_spider(zap, target)
    zap = zap_auth_ajax_spider(zap, target)
    zap = zap_passive(zap)
    zap = zap_auth_active(zap, target)

    fn = '{}_ui_zap_report.xml'.format(project)
    zap_write(zap, fn)

    return fn    

def compliance_scan(project, target, scan='zap-baseline'):
    if scan == 'auth-scan':
        file_name = zap_auth(project, target)
    elif scan == 'api-scan':
        file_name = zap_api(project, target)
    elif scan == 'ui-scan':
        file_name = zap_ui(project, target)
    else:
        file_name = zap_baseline(project, target)
    return file_name