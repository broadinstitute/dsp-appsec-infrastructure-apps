"""
Provides high-level methods to interface with ZAP.
"""

import logging
import os
import shutil
from enum import Enum
from urllib.parse import urlparse

import google.auth
import requests
import terra_auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from zap_common import (wait_for_zap_start, write_report, zap_access_target,
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

def parse_url(url):
    """
    Helper function for parsing the target URL into component parts.

    Returns:
    string: hostname, int: port, string: path
    """
    url_parts = urlparse(url)
    parsed_hostname = url_parts.hostname
    parsed_path = url_parts.path
    parsed_port = url_parts.port

    return parsed_hostname, parsed_port, parsed_path


def zap_sa_auth(zap: ZAPv2, env, target):
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
        url=target + ".*"
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
    return token


def leo_auth(host, path, token):
    """
    Set up cookie auth for leo apps.
    """
    logging.info("Authenticating to Leo...")
    # Leo apps if already launched have a separate domain from Leo.
    # And there's a workspace id after the host. https://custom.host/workspaceId/apiEndPoints

    # Make a request to host/first part of path//setCookie with bearer token header
    path_parts = path.split('/')
    if len(path_parts) > 1:
        target_dir = path_parts[1]
    else:
        # Leo endpoint is /proxy//setCookie
        target_dir = "proxy"
    set_cookie_endpoint = f"https://{host}/{target_dir}//setCookie"
    headers = {"Authorization": token}
    response = requests.get(set_cookie_endpoint, headers=headers, timeout=10)
    if response.status_code == 200:
        return True
    return False

def zap_setup_cookie(zap, domain, context_ID):
    """
    Zap needs to be told to use cookies while scanning.
    This can be done within a context.
    """
    # Copied from dsp-appsec-zap-automation
    username = "testuser"
    zap.users.new_user(context_ID, username)
    userid = zap.users.users_list(context_ID)[0]["id"]
    # This is the secret sauce for using cookies.
    # The user above is now associated with the active cookie.
    # It should always choose the newest one.
    sessions=zap.httpsessions.sessions(site = domain)
    session_name=sessions[-1]["session"][0]
    zap.users.set_authentication_credentials(context_ID,userid,"sessionName=" + session_name)

    zap.users.set_user_enabled(context_ID,userid,True)
    zap.forcedUser.set_forced_user(context_ID,userid)
    zap.forcedUser.set_forced_user_mode_enabled(True)
    return username, userid


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
    LEOAPP = "LeoApp"

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

    host, port, path = parse_url(target_url)

    zap = zap_init(zap_port, target_url)
    env = "prod" #set prod as default
    if "dev" in host:
        env = "dev"
    # ZAP scans should be run in a context. This provides a scope for the scan,
    # and can provide more granular authentication controls.

    # Scan types:
    # BASELINE - unauthenticated, no active scan.
    # API - authenticated with SA, imports openid config, active scan is performed.
    # UI - authenticated with SA, active scan and ajax spider is performed.
    # AUTH - authenticated with SA, active scan is performed.
    
    # Set up context for scan
    zap.context.new_context(project)
    context_ID = zap.context.context(project)["id"]
    zap.authentication.set_authentication_method(context_ID,"manualAuthentication")

    zap.context.include_in_context(project, ".*" + host + ".*")


    if scan_type != ScanType.BASELINE:
        token = zap_sa_auth(zap, env, target_url)
        if scan_type == ScanType.LEOAPP:
            leo_auth(host, path, token)
            cookie_name = "LeoToken"
            zap.httpsessions.add_default_session_token(cookie_name)
            # Sets a user in the context with the cookie, and forces all Zap requests to use that cookie
            zap_setup_cookie(zap, host, context_ID)

    if scan_type == ScanType.API:
        zap_api_import(zap, target_url)

    zap.spider.scan(contextname=project,url=target_url)

    if scan_type == ScanType.UI:
        zap.ajaxSpider.scan(target_url, contextname=project)

    zap_wait_for_passive_scan(zap, timeout_in_secs=TIMEOUT_MINS * 60)

    if scan_type != ScanType.BASELINE:
        zap.ascan.scan(target_url, contextid=context_ID, recurse=True)

    filename = zap_report(zap, project, scan_type)
    session_file = zap_save_session(zap, project, scan_type)

    return (filename, session_file)
