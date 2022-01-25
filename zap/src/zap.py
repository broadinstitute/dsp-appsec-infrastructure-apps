"""
Provides high-level methods to interface with ZAP.
"""

import logging
import os
import shutil
from enum import Enum

from zapv2 import ZAPv2
import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from zap_common import (wait_for_zap_start, write_report, zap_access_target,
                        zap_active_scan, zap_ajax_spider, zap_spider,
                        zap_wait_for_passive_scan)


TIMEOUT_MINS = 5


def zap_connect(zap_port: int):
    """
    Connect to the Zap instance
    """
    proxy = f"http://localhost:{zap_port}"
    zap = ZAPv2(proxies={"http": proxy, "https": proxy})
    wait_for_zap_start(zap, timeout_in_secs=TIMEOUT_MINS * 60)
    return zap


def zap_init(zap_port: int, target_url: str):
    """
    Connect to ZAP service running on localhost.
    """
    zap = zap_connect(zap_port)
    zap.core.new_session(name='zap_session', overwrite=True)
    logging.info("Accessing target %s", target_url)
    zap_access_target(zap, target_url)

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


def zap_api_import(zap: ZAPv2, target_url: str):
    """
    Import OpenAPI definition from target URL.
    """
    start_urls = zap.core.urls()
    res = zap.openapi.import_url(target_url)
    if zap.core.urls() == start_urls:
        raise RuntimeError(f"Failed to import API from {target_url}: {res}")


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


class ScanType(str, Enum):
    """
    Enumerates Zap compliance scan types
    """

    API = "API"
    AUTH = "Authenticated"
    BASELINE = "Baseline"
    UI = "UI"

    def __str__(self):
        return str(self.name).lower()

    def label(self):
        """"Get user-friendly name of the scan type"""
        return str(self.value)


def zap_report(zap: ZAPv2, project: str, scan_type: ScanType):
    """
    Generate ZAP scan XML report.
    """
    zap.core.set_option_merge_related_alerts(True)

    filename = f"{project}_{scan_type}-scan_report.xml"
    filename = filename.replace("-", "_").replace(" ", "")
    write_report(filename, zap.core.xmlreport())

    return filename

def zap_save_session(zap: ZAPv2, project: str, scan_type: ScanType):
    """
    Save and zip zap session.
    """
    os.mkdir(os.getcwd()+"/session")
    session_folder = os.getcwd()+"/session/"
    session_filename = f"{project}_{scan_type}-session"
    session_filename = session_filename.replace("-", "_").replace(" ", "")
    zap.core.save_session(session_folder+session_filename)
    shutil.make_archive(session_filename, 'zip' , session_folder)
    return session_filename + ".zip"


def zap_compliance_scan(
    project: str,
    zap_port: int,
    target_url: str,
    scan_type: ScanType = ScanType.BASELINE,
):
    """
    Run a ZAP compliance scan of a given type against the target URL.
    """
    zap = zap_init(zap_port, target_url)

    if scan_type != ScanType.BASELINE:
        zap_auth(zap)

    if scan_type == ScanType.API:
        zap_api_import(zap, target_url)

    zap_spider(zap, target_url)

    if scan_type == ScanType.UI:
        zap_ajax_spider(zap, target_url, max_time=TIMEOUT_MINS)

    zap_wait_for_passive_scan(zap, timeout_in_secs=TIMEOUT_MINS * 60)

    if scan_type == ScanType.UI:
        zap_active_scan(zap, target_url, None)

    filename = zap_report(zap, project, scan_type)
    sessionFile = zap_save_session(zap, project, scan_type)

    return (filename, sessionFile)
