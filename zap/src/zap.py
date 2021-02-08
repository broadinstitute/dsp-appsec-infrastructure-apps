# The modules includes
# - method to fetch an access token (for running scans as a authenticated user)
# - individual "steps" of each zap scans
# - "complete" scans that include different steps depending on the type of scan
# - a "compliance scan" method that takes a project, url, and scan type, and returns a filename

import os
import sys
import time

import google.auth
import google.auth.transport.requests
from requests.exceptions import ProxyError
from urllib3.exceptions import NewConnectionError
from zapv2 import ZAPv2

def get_gc_token():
    credentials, __ = google.auth.default(
        scopes=[
            'profile', 'email', 'openid',
            'https://www.googleapis.com/auth/cloud-billing',
        ])
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


def zap_retry(function, exception):
    timeout = time.time() + 60*10
    while time.time() < timeout:
        try:
            function()
            return True
        except exception:
            time.sleep(5)
    return False


def zap_init(project, target):
    # Connect to ZAP
    owasp_key = ''  # currently disabled
    host = '127.0.0.1'
    port = os.getenv('ZAP_PORT')
    proxy = f'http://{host}:{port}'
    zap = ZAPv2(apikey=owasp_key, proxies={'http': proxy, 'https': proxy})

    if not zap_retry(lambda: zap.context.new_context(project, owasp_key), ProxyError) or \
            not zap_retry(lambda: zap.urlopen(target), NewConnectionError):
        print("Zap Daemon Timeout")
        sys.exit(1)
    return zap


def zap_auth(zap):
    print("Authenticating via Replacer...")
    token = get_gc_token()
    bearer = f"Bearer {token}"
    zap.replacer.add_rule(description="auth", enabled=True, matchtype="REQ_HEADER",
                          matchregex=False, matchstring="Authorization", replacement=bearer)
    return zap


def wait_for_scan(zap, scanner, minutes, is_auth=False, scan_id=None):
    time.sleep(5)
    start = time.time()
    timeout = time.time() + 60*minutes  # timeout is x minutes from now
    while ((scan_id != None and int(scanner.status(scan_id)) < 100)
           or (scanner.status == 'running')):
        time.sleep(2)
        if time.time() > timeout:
            break
        if is_auth and (time.time() - start) > 1800:
            zap = zap_auth(zap)


def zap_access(zap, target):
    # Proxy a request to the target so that ZAP has something to deal with
    print(f'Accessing target {target}')
    zap.urlopen(target)
    # Give the sites tree a chance to get updated
    time.sleep(2)
    return zap


def zap_spider(zap, target, is_auth=False):
    if is_auth:
        zap = zap_auth(zap)
    print(f'Spidering target {target}')
    scanid = zap.spider.scan(target)
    wait_for_scan(zap, zap.spider, 5, is_auth, scanid)
    print('Spider completed')
    return zap


def zap_ajax_spider(zap, target, is_auth=False):
    print(f'Ajax Spider target {target}')
    zap = zap_auth(zap)
    zap.ajaxSpider.scan(target)
    wait_for_scan(zap, zap.ajaxSpider, 5, is_auth)
    print('Ajax Spider completed')
    return zap


def zap_passive(zap):
    while (int(zap.pscan.records_to_scan) > 0):
        print(f'Records to passive scan : {zap.pscan.records_to_scan}')
        time.sleep(2)

    print('Passive Scan completed')
    return zap


def zap_active(zap, target, is_auth=False):
    print(f'Active Scanning target {target}')
    scanid = zap.ascan.scan(target)
    wait_for_scan(zap, zap.ascan, 60, is_auth, scanid)
    return zap


def zap_write(zap, fn):
    zap.core.set_option_merge_related_alerts(True)
    with open(fn, 'wb') as f:
        f.write(zap.core.xmlreport().encode('utf-8'))
    return zap


def compliance_scan(project, target, scan='baseline-scan'):
    is_auth = scan != 'baseline-scan'
    zap = zap_init(project, target)
    zap = zap_access(zap, target)
    if scan == 'api-scan':
        token = get_gc_token()
        zap.openapi.import_url(url=target, hostoverride=None, apikey=token)
    zap = zap_spider(zap, target, is_auth)
    if scan == 'ui-scan':
        zap = zap_ajax_spider(zap, target, is_auth)
    zap = zap_passive(zap)
    if scan == 'ui-scan':
        zap = zap_active(zap, target, is_auth)

    file_name = f'{project}_{scan}_report.xml'.replace("-", "_").replace(" ", "")
    zap = zap_write(zap, file_name)
    zap.core.shutdown()

    return file_name
