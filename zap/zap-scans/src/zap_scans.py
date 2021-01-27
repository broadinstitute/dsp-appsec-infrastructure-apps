#!/usr/bin/env python3
# The modules includes
# - method to fetch an access token (for running scans as a authenticated user)
# - individual "steps" of each zap scans
# - "complete" scans that include different steps depending on the type of scan
# - a "compliance scan" method that takes a project, url, and scan type, and returns a filename
import time, os
from zapv2 import ZAPv2
import google.auth
import google.auth.transport.requests

def get_gc_token():
    credentials, __ = google.auth.default(
    scopes=[
            'profile', 'email', 'openid',
            'https://www.googleapis.com/auth/cloud-billing',
        ])
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

def zap_init(project, target):
    # Connect to ZAP
    owasp_key = '' # currently disabled
    host = '127.0.0.1'
    port = os.getenv('ZAP_PORT')
    proxy = f'http://{host}:{port}'
    zap = ZAPv2(apikey=owasp_key, proxies={'http': proxy, 'https': proxy})

    zap.context.new_context(project, owasp_key)

    zap_listening = False
    timeout = time.time() + 60*10
    while time.time() < timeout:
        print("Waiting for Zap daemon to start...")
        try:
            zap.urlopen(target)
            zap_listening = True
        except Exception: 
            pass
        time.sleep(5)

    if zap_listening == False:
        print("Zap Daemon Timeout")
        exit(1)
    return zap

def zap_auth(zap):
    print("Authenticating via Replacer...")
    token = get_gc_token()
    bearer = f"Bearer {token}"
    zap.replacer.add_rule(description="auth", enabled=True, matchtype="REQ_HEADER", matchregex=False, matchstring="Authorization", replacement=bearer)
    return zap

def zap_access(zap, target):
    # Proxy a request to the target so that ZAP has something to deal with
    print(f'Accessing target {target}')
    zap.urlopen(target)
    # Give the sites tree a chance to get updated
    time.sleep(2)
    return zap

def zap_spider(zap, target):
    print(f'Spidering target {target}')
    scanid = zap.spider.scan(target)
    # Give the Spider a chance to start
    time.sleep(2)
    while (int(zap.spider.status(scanid)) < 100):
        time.sleep(2)

    print ('Spider completed')
    return zap

def zap_auth_spider(zap, target):
    zap = zap_auth(zap)
    print(f'Spidering target {target}')
    scanid = zap.spider.scan(target)
    # Give the Spider a chance to start
    time.sleep(2)
    count = 2
    while (int(zap.spider.status(scanid)) < 100):
        # Loop until the spider has finished
        print(f'Spider progress %: {zap.spider.status(scanid)}')
        time.sleep(2)
        count += 2
        if count > 1800:
            zap = zap_auth(zap)
            count = 0

    print ('Spider completed')
    return zap

def zap_auth_ajax_spider(zap, target):
    print(f'Ajax Spider target {target}')
    zap = zap_auth(zap)
    zap.ajaxSpider.scan(target)
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
        print (f'Records to passive scan : {zap.pscan.records_to_scan}')
        time.sleep(2)

    print ('Passive Scan completed')
    return zap

def zap_auth_active(zap, target):
    zap = zap_auth(zap)

    print (f'Active Scanning target {target}')
    scanid = zap.ascan.scan(target)
    count = 0
    while (int(zap.ascan.status(scanid)) < 100):
        # Loop until the scanner has finished
        print (f'Scan progress %: {zap.ascan.status(scanid)}')
        time.sleep(5)
        count += 5
        if count > 1800:
            zap = zap_auth(zap)
            count = 0

    print ('Active Scan completed')

    return zap

def zap_active(zap, target):
    print (f'Active Scanning target {target}')
    scanid = zap.ascan.scan(target)
    while (int(zap.ascan.status(scanid)) < 100):
        # Loop until the scanner has finished
        print (f'Scan progress %: {zap.ascan.status(scanid)}')
        time.sleep(5)

    print ('Active Scan completed')

    return zap

def zap_write(zap, fn):
    with open(fn, 'wb') as f:
        f.write(zap.core.xmlreport().encode('utf-8'))
    return zap

def zap_baseline_scan(project, target):

    zap = zap_init(project, target)
    zap = zap_access(zap, target)
    zap = zap_spider(zap, target)
    zap = zap_passive(zap)

    fn = f'{project}_baseline_zap_report.xml'
    zap = zap_write(zap, fn)
    zap.core.shutdown()

    return fn

def zap_auth_scan(project, target):

    zap = zap_init(project, target)
    zap = zap_access(zap, target)
    zap = zap_auth_spider(zap, target)
    zap = zap_passive(zap)

    fn = f'{project}_auth_zap_report.xml'
    zap = zap_write(zap, fn)
    zap.core.shutdown()

    return fn

def zap_api_scan(project, target):

    zap = zap_init(project, target)
    zap = zap_access(zap, target)
    token = get_gc_token()
    zap.openapi.import_url(url=target, hostoverride=None, apikey=token)
    zap = zap_auth_spider(zap, target)
    zap = zap_passive(zap)
    zap = zap_auth_active(zap, target)

    fn = f'{project}_api_zap_report.xml'
    zap = zap_write(zap, fn)
    zap.core.shutdown()

    return fn

def zap_ui_scan(project, target):

    zap = zap_init(project, target)
    zap = zap_access(zap, target)
    zap = zap_auth_spider(zap, target)
    zap = zap_auth_ajax_spider(zap, target)
    zap = zap_passive(zap)
    zap = zap_auth_active(zap, target)

    fn = f'{project}_ui_zap_report.xml'
    zap = zap_write(zap, fn)
    zap.core.shutdown()

    return fn

def compliance_scan(project, target, scan='baseline-scan'):
    if scan == 'auth-scan':
        file_name = zap_auth_scan(project, target)
    elif scan == 'api-scan':
        file_name = zap_api_scan(project, target)
    elif scan == 'ui-scan':
        file_name = zap_ui_scan(project, target)
    else:
        file_name = zap_baseline_scan(project, target)
    return file_name
