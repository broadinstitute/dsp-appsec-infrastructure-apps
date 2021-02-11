# The modules includes
# - method to fetch an access token (for running scans as a authenticated user)
# - individual "steps" of each zap scans
# - "complete" scans that include different steps depending on the type of scan
# - a "compliance scan" method that takes a project, url, and scan type, and returns a filename

import logging
import os
import time
from enum import Enum
from typing import Callable

import google.auth
import google.auth.transport.requests
from zapv2 import ZAPv2, spider


def get_gcp_token() -> str:
    credentials, _ = google.auth.default(
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


def retry(function: Callable, *args):
    timeout = time.time() + 60 * 10
    while time.time() < timeout:
        try:
            function(*args)
            return
        except ConnectionRefusedError:
            time.sleep(5)
    raise TimeoutError("Zap Proxy timeout")


def zap_init(context: str):
    # Connect to ZAP
    owasp_key = ""  # currently disabled
    host = "127.0.0.1"
    port = os.getenv("ZAP_PORT")
    proxy = f"http://{host}:{port}"
    zap = ZAPv2(apikey=owasp_key, proxies={"http": proxy, "https": proxy})

    retry(zap.context.new_context, context, owasp_key)

    return zap


def zap_auth(zap: ZAPv2):
    logging.info("Authenticating via Replacer...")
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


def wait_for_scan(
    zap: ZAPv2, scanner: spider, minutes: int, is_auth=False, scan_id=None
):
    time.sleep(5)
    start = time.time()
    timeout = time.time() + 60 * minutes  # timeout is x minutes from now
    while (scan_id is not None and int(scanner.status(scan_id)) < 100) or (
        scanner.status == "running"
    ):
        time.sleep(2)
        if time.time() > timeout:
            break
        if is_auth and (time.time() - start) > 1800:
            zap_auth(zap)


def zap_access(zap: ZAPv2, target_url: str):
    # Proxy a request to the target URL so that ZAP has something to deal with
    logging.info("Accessing target URL %s", target_url)
    result = zap.urlopen(target_url)
    if result.startswith("ZAP Error"):
        raise RuntimeError(result)
    # Give the sites tree a chance to get updated
    time.sleep(2)


def zap_spider(zap: ZAPv2, target_url: str, is_auth: bool = False):
    if is_auth:
        zap_auth(zap)
    logging.info("Spidering target %s", target_url)
    scan_id = zap.spider.scan(target_url)
    wait_for_scan(zap, zap.spider, 5, is_auth, scan_id)
    logging.info("Spider completed")


def zap_ajax_spider(zap: ZAPv2, target_url: str, is_auth: bool = False):
    logging.info("Ajax Spider target %s", target_url)
    zap_auth(zap)
    zap.ajaxSpider.scan(target_url)
    wait_for_scan(zap, zap.ajaxSpider, 5, is_auth)
    logging.info("Ajax Spider completed")


def zap_passive(zap: ZAPv2):
    while int(zap.pscan.records_to_scan) > 0:
        logging.info("Records to passive scan: %s", zap.pscan.records_to_scan)
        time.sleep(2)

    logging.info("Passive Scan completed")


def zap_active(zap: ZAPv2, target_url: str, is_auth: bool = False):
    logging.info("Active Scanning target %s", target_url)
    scan_id = zap.ascan.scan(target_url)
    wait_for_scan(zap, zap.ascan, 60, is_auth, scan_id)


def zap_write(zap: ZAPv2, file_name: str):
    zap.core.set_option_merge_related_alerts(True)
    with open(file_name, "wb") as file:
        file.write(zap.core.xmlreport().encode("utf-8"))


class ScanType(str, Enum):
    API = "api"
    AUTH = "auth"
    BASELINE = "baseline"
    UI = "ui"

    def __str__(self):
        return str(self.value)


def compliance_scan(
    project: str, target_url: str, scan_type: ScanType = ScanType.BASELINE
):
    is_auth = scan_type != ScanType.BASELINE
    zap = zap_init(project)
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

    file_name = f"{project}_{scan_type}-scan_report.xml"
    file_name = file_name.replace("-", "_").replace(" ", "")
    zap_write(zap, file_name)
    zap.core.shutdown()

    return file_name
