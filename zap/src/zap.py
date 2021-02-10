# The modules includes
# - method to fetch an access token (for running scans as a authenticated user)
# - individual "steps" of each zap scans
# - "complete" scans that include different steps depending on the type of scan
# - a "compliance scan" method that takes a project, url, and scan type, and returns a filename

import os
import sys
import time
from enum import Enum
from typing import Callable

import google.auth
import google.auth.transport.requests
from requests.exceptions import ProxyError
from urllib3.exceptions import NewConnectionError
from zapv2 import ZAPv2


def get_gcp_token() -> str:
    credentials, __ = google.auth.default(
        scopes=[
            "profile",
            "email",
            "openid",
            "https://www.googleapis.com/auth/cloud-billing",
        ]
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


def zap_retry(function: Callable, exception):
    timeout = time.time() + 60 * 10
    while time.time() < timeout:
        try:
            function()
            return True
        except exception:
            time.sleep(5)
    return False


def zap_init(context: str, target_url: str):
    # Connect to ZAP
    owasp_key = ""  # currently disabled
    host = "127.0.0.1"
    port = os.getenv("ZAP_PORT")
    proxy = f"http://{host}:{port}"
    zap = ZAPv2(apikey=owasp_key, proxies={"http": proxy, "https": proxy})

    if not zap_retry(
        lambda: zap.context.new_context(context, owasp_key), ProxyError
    ) or not zap_retry(lambda: zap.urlopen(target_url), NewConnectionError):
        print("Zap Daemon Timeout")
        sys.exit(1)
    return zap


def zap_auth(zap: ZAPv2):
    print("Authenticating via Replacer...")
    token = get_gcp_token()
    bearer = f"Bearer {token}"
    zap.replacer.add_rule(
        description="auth",
        enabled=True,
        matchtype="REQ_HEADER",
        matchregex=False,
        matchstring="Authorization",
        replacement=bearer,
    )


def wait_for_scan(zap: ZAPv2, scanner, minutes, is_auth=False, scan_id=None):
    time.sleep(5)
    start = time.time()
    timeout = time.time() + 60 * minutes  # timeout is x minutes from now
    while (scan_id != None and int(scanner.status(scan_id)) < 100) or (
        scanner.status == "running"
    ):
        time.sleep(2)
        if time.time() > timeout:
            break
        if is_auth and (time.time() - start) > 1800:
            zap_auth(zap)


def zap_access(zap: ZAPv2, target: str):
    # Proxy a request to the target so that ZAP has something to deal with
    print(f"Accessing target {target}")
    zap.urlopen(target)
    # Give the sites tree a chance to get updated
    time.sleep(2)


def zap_spider(zap: ZAPv2, target_url: str, is_auth: bool = False):
    if is_auth:
        zap_auth(zap)
    print(f"Spidering target {target_url}")
    scanid = zap.spider.scan(target_url)
    wait_for_scan(zap, zap.spider, 5, is_auth, scanid)
    print("Spider completed")


def zap_ajax_spider(zap: ZAPv2, target_url: str, is_auth: bool = False):
    print(f"Ajax Spider target {target_url}")
    zap_auth(zap)
    zap.ajaxSpider.scan(target_url)
    wait_for_scan(zap, zap.ajaxSpider, 5, is_auth)
    print("Ajax Spider completed")


def zap_passive(zap: ZAPv2):
    while int(zap.pscan.records_to_scan) > 0:
        print(f"Records to passive scan : {zap.pscan.records_to_scan}")
        time.sleep(2)

    print("Passive Scan completed")


def zap_active(zap: ZAPv2, target_url: str, is_auth: bool = False):
    print(f"Active Scanning target {target_url}")
    scanid = zap.ascan.scan(target_url)
    wait_for_scan(zap, zap.ascan, 60, is_auth, scanid)


def zap_write(zap: ZAPv2, file_name: str):
    zap.core.set_option_merge_related_alerts(True)
    with open(file_name, "wb") as f:
        f.write(zap.core.xmlreport().encode("utf-8"))


class ScanType(str, Enum):
    API = "api"
    AUTH = "auth"
    BASELINE = "baseline"
    UI = "ui"


def compliance_scan(
    project: str, target_url: str, scan_type: ScanType = ScanType.BASELINE
):
    is_auth = scan_type != ScanType.BASELINE
    zap = zap_init(project, target_url)
    zap_access(zap, target_url)
    if scan_type == ScanType.API:
        token = get_gcp_token()
        zap.openapi.import_url(url=target_url, hostoverride=None, apikey=token)
    zap_spider(zap, target_url, is_auth)
    if scan_type == ScanType.UI:
        zap_ajax_spider(zap, target_url, is_auth)
    zap_passive(zap)
    if scan_type == ScanType.UI:
        zap_active(zap, target_url, is_auth)

    file_name = f"{project}_{scan_type.value}_report.xml".replace("-", "_").replace(
        " ", ""
    )
    zap_write(zap, file_name)
    zap.core.shutdown()

    return file_name
