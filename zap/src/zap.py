"""
Provides high-level methods to interface with ZAP.
"""

import logging
import os
from enum import Enum

import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from zapv2 import ZAPv2

import zap_common
from zap_common import (
    wait_for_zap_start,
    zap_access_target,
    zap_active_scan,
    zap_ajax_spider,
    zap_spider,
    zap_wait_for_passive_scan,
)


def zap_init(context: str, target_url: str):
    """
    Connect to ZAP service running on localhost.
    """
    port = os.getenv("ZAP_PORT")
    proxy = f"http://localhost:{port}"
    zap = ZAPv2(proxies={"http": proxy, "https": proxy})
    wait_for_zap_start(zap, timeout_in_secs=60)

    zap.context.new_context(context)
    zap_common.context_name = context

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

    if scan_type != ScanType.BASELINE:
        zap_auth(zap)

    if scan_type == ScanType.API:
        zap.openapi.import_url(target_url)

    zap_spider(zap, target_url)

    if scan_type == ScanType.UI:
        zap_ajax_spider(zap, target_url, max_time=5)

    zap_wait_for_passive_scan(zap, timeout_in_secs=5 * 60)

    if scan_type == ScanType.UI:
        zap_active_scan(zap, target_url, None)

    filename = zap_report(zap, context, scan_type)
    zap.core.shutdown()

    return filename
