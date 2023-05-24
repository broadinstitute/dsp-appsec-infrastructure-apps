"""
Provides high-level methods to interface with ZAP.
"""

import logging
import os
import shutil
from enum import Enum

import google.auth
import terra_auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from zap_common import (wait_for_zap_start, write_report, zap_access_target,
                        zap_active_scan, zap_ajax_spider, zap_spider,
                        zap_wait_for_passive_scan)
from zapv2 import ZAPv2

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
    # replace with api call to core.accessUrl
    zap_access_target(zap, target_url)

    return zap


def zap_sa_auth(zap: ZAPv2, env):
    """
    Set up Google token auth for ZAP requests.
    """
    logging.info("Authenticating via Replacer...")
    token = get_gcp_token()
    bearer = f"Bearer {token}"
    success = False
    zap.replacer.add_rule(
        description="auth",
        enabled=True,
        matchtype="REQ_HEADER",
        matchregex=False,
        matchstring="Authorization",
        replacement=bearer,
    )
    # checks to see if the user is logged in, registered,
    # and has signed the TOS.
    success = terra_auth.terra_register_sa(bearer, env)
    if success:
        logging.info("ZAP Service Account is registered with Terra.")
        tos = terra_auth.terra_tos(bearer, env)
        if tos:
            logging.info("SA has accepted the TOS.")
    else:
        logging.info("ZAP Service Account failed to register with Terra.")
        return
    



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
    share_path = os.getenv("VOLUME_SHARE")
    share_path_sess = share_path+"/session/"
    session_filename = f"{project}_{scan_type}-session"
    session_filename = session_filename.replace("-", "_").replace(" ", "")
    # zap scanner container saves session to shared volume
    zap.core.save_session(share_path_sess+session_filename)
    # scan controller uses same shared volume to zip session and return the filename
    try:
        shutil.make_archive(session_filename, 'zip' , share_path_sess)
    except BaseException as base_error: # pylint: disable=bare-except
        print("Unable to zip session file.")
        raise base_error
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
    env = "prod" #set prod as default
    if "dev" in target_url:
        env = "dev"
    # ZAP scans should be run in a context. This provides a scope for the scan,
    # and can provide more granular authentication controls.

    # Scan types:
    # BASELINE - unauthenticated, no active scan.
    # API - authenticated with SA, imports openid config, active scan is performed.
    # UI - authenticated with SA, active scan and ajax spider is performed.
    # AUTH - authenticated with SA, active scan is performed.

    if scan_type != ScanType.BASELINE:
        zap_sa_auth(zap, env)

    if scan_type == ScanType.API:
        zap_api_import(zap, target_url)

    zap_spider(zap, target_url)

    if scan_type == ScanType.UI:
        zap_ajax_spider(zap, target_url, max_time=TIMEOUT_MINS)

    zap_wait_for_passive_scan(zap, timeout_in_secs=TIMEOUT_MINS * 60)

    if scan_type != ScanType.BASELINE:
        zap_active_scan(zap, target_url, None)

    filename = zap_report(zap, project, scan_type)
    session_file = zap_save_session(zap, project, scan_type)

    return (filename, session_file)
