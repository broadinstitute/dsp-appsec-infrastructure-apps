"""
Provides high-level methods to interface with ZAP.
"""

import logging
import os
import time
from enum import Enum
from typing import Callable

import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from zapv2 import ZAPv2, spider


def get_gcp_token() -> str:
    """
    Generate a Google access token with custom scopes for the default identity.
    """
    credentials, _ = google.auth.default(
        scopes=[
            "profile",
            "email",
            "openid",
            "https://www.googleapis.com/auth/cloud-billing",
        ]
    )
    credentials.refresh(GoogleAuthRequest())
    return credentials.token


def retry(function: Callable, *args):
    """
    Retry a function until a timeout.
    """
    timeout = time.time() + 60 * 10
    while time.time() < timeout:
        try:
            function(*args)
            return
        except ConnectionRefusedError:
            time.sleep(5)
    raise TimeoutError("ZAP Proxy timeout")


def zap_access(zap: ZAPv2, target_url: str):
    """
    Proxy a request to the target URL to test the connection to ZAP.
    """
    logging.info("Accessing target URL %s", target_url)
    result = zap.urlopen(target_url)
    if result.startswith("ZAP Error"):
        raise RuntimeError(result)
    time.sleep(2)  # give the sites tree a chance to get updated


def zap_init(context: str, target_url: str):
    """
    Connect to ZAP service running on localhost.
    """
    port = os.getenv("ZAP_PORT")
    proxy = f"http://localhost:{port}"
    zap = ZAPv2(proxies={"http": proxy, "https": proxy})

    retry(zap.context.new_context, context)
    zap_access(zap, target_url)

    return zap


def zap_auth(zap: ZAPv2):
    """
    Set up Google token auth for ZAP requests.
    """
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
    """
    Wait for a ZAP scan to be completed.
    """
    time.sleep(5)
    start = time.time()
    timeout = start + 60 * minutes
    while (scan_id is not None and int(scanner.status(scan_id)) < 100) or (
        scanner.status == "running"
    ):
        time.sleep(2)
        now = time.time()
        if now > timeout:
            break
        if is_auth and now > start + 60 * 30:
            zap_auth(zap)


def zap_spider(zap: ZAPv2, target_url: str, is_auth: bool = False):
    """
    Call ZAP spider and wait for completion.
    """
    if is_auth:
        zap_auth(zap)
    logging.info("Spidering target %s", target_url)
    scan_id = zap.spider.scan(target_url)
    wait_for_scan(zap, zap.spider, 5, is_auth, scan_id)
    logging.info("Spider completed")


def zap_ajax_spider(zap: ZAPv2, target_url: str, is_auth: bool = False):
    """
    Call ZAP AJAX spider and wait for completion.
    """
    logging.info("Ajax Spider target %s", target_url)
    zap_auth(zap)
    zap.ajaxSpider.scan(target_url)
    wait_for_scan(zap, zap.ajaxSpider, 5, is_auth)
    logging.info("Ajax Spider completed")


def zap_passive(zap: ZAPv2):
    """
    Wait for ZAP passive scan completion.
    """
    while int(zap.pscan.records_to_scan) > 0:
        logging.info("Records to passive scan: %s", zap.pscan.records_to_scan)
        time.sleep(2)
    logging.info("Passive Scan completed")


def zap_active(zap: ZAPv2, target_url: str, is_auth: bool = False):
    """
    Trigger ZAP active scan and wait for completion.
    """
    logging.info("Active Scanning target %s", target_url)
    scan_id = zap.ascan.scan(target_url)
    wait_for_scan(zap, zap.ascan, 60, is_auth, scan_id)


class ScanType(str, Enum):
    """
    Enumerates Zap compliance scan types
    """

    API = "api"
    AUTH = "auth"
    BASELINE = "baseline"
    UI = "ui"

    def __str__(self):
        return str(self.value)


def zap_report(zap: ZAPv2, context: str, scan_type: ScanType):
    """
    Generate ZAP scan XML report.
    """
    zap.core.set_option_merge_related_alerts(True)

    filename = f"{context}_{scan_type}-scan_report.xml"
    filename = filename.replace("-", "_").replace(" ", "")

    with open(filename, "wb") as file:
        file.write(zap.core.xmlreport().encode("utf-8"))

    return filename


def zap_compliance_scan(
    context: str, target_url: str, scan_type: ScanType = ScanType.BASELINE
):
    """
    Run a ZAP compliance scan of a given type against the target URL.
    """
    zap = zap_init(context, target_url)
    is_auth = scan_type != ScanType.BASELINE

    if scan_type == ScanType.API:
        token = get_gcp_token()
        zap.openapi.import_url(url=target_url, apikey=token)

    zap_spider(zap, target_url, is_auth)

    if scan_type == ScanType.UI:
        zap_ajax_spider(zap, target_url, is_auth)

    zap_passive(zap)

    if scan_type == ScanType.UI:
        zap_active(zap, target_url, is_auth)

    filename = zap_report(zap, context, scan_type)
    zap.core.shutdown()

    return filename
