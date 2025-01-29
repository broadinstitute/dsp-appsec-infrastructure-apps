"""
Provides high-level methods to interface with ZAP.
"""

import base64
import json
import logging
import os
import shutil
from datetime import datetime
import time
import jwt
from urllib.parse import urlparse, urlencode

import google.auth
import requests
import terra_auth
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token
from zap_common import (wait_for_zap_start, zap_access_target,
                        zap_wait_for_passive_scan)
from zap_scan_type import ScanType
from zapv2 import ZAPv2

TIMEOUT_MINS = 5
zap_port = int(os.getenv("ZAP_PORT", ""))
PROXY = f"http://localhost:{zap_port}"


def zap_connect():
    """
    Connect to the Zap instance
    """
    zap = ZAPv2(proxies={"http": PROXY, "https": PROXY}, apikey=os.getenv("ZAP_API_KEY", ""))
    wait_for_zap_start(zap, timeout_in_secs=TIMEOUT_MINS * 60)
    return zap


def zap_init(target_url: str):
    """
    Connect to ZAP service running on localhost.
    """
    zap = zap_connect()
    zap.core.new_session(name='zap_session', overwrite=True)
    logging.info("Accessing target %s", target_url)
    # Rate limit scan to avoid overwhleming sites
    description = "max_requests"
    enabled = True
    matchregex = True
    matchstring = ".*"
    requestspersecond = 5
    groupby = "host"
    zap.network.add_rate_limit_rule(description,
                                    enabled,
                                    matchregex,
                                    matchstring,
                                    requestspersecond,
                                    groupby)

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


def zap_setup_context(zap, project, host):
    """
    Setup context and scope for scan
    """

    zap.context.new_context(project)
    context_id = zap.context.context(project)["id"]
    zap.authentication.set_authentication_method(context_id, "manualAuthentication")
    zap.context.include_in_context(project, ".*" + host + ".*")
    return context_id


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
        replacement=bearer
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
        logging.error("ZAP Service Account failed to register with Terra.")
    return token


def leo_auth(host, path, token):
    """
    Set up cookie auth for leo apps.
    """
    proxies = {
        'http': PROXY,
        'https': PROXY,
        }

    zap = zap_connect()
    zap.httpsessions.add_default_session_token("LeoToken")
    logging.info("Authenticating to Leo...")
    # Leo apps if already launched have a separate domain from Leo.
    # And there's a workspace id after the host.
    # https://custom.host/workspaceId/apiEndPoints
    # Make a request to host/first part of path//setCookie
    # with bearer token header
    path_parts = path.split('/')
    if len(path_parts) > 1:
        target_dir = path_parts[1]
    else:
        # Leo endpoint is /proxy//setCookie
        logging.info("Using the default proxy directory for setCookie")
        target_dir = "proxy"

    logging.info("Using the setCookie endpoint to set the cookie.")
    set_cookie_endpoint = f"https://{host}/{target_dir}//setCookie"
    headers = {"Authorization": token,
               "Referer": f"https://{host}/"}
    # verify is set to false in order to proxy requests through ZAP
    response = requests.get(set_cookie_endpoint, headers=headers,
                            timeout=25, proxies=proxies, verify=False)
    logging.info(response.text)
    if response.status_code == 204:
        logging.info("Set cookie was successful")
        return True
    logging.error("Set cookie did not succeed")
    return False


def zap_setup_cookie(zap, domain, context_id, cookie_name=None):
    """
    Zap needs to be told to use cookies while scanning.
    This can be done within a context.
    """
    try:
        # Copied from dsp-appsec-zap-automation
        logging.info("Set up test user in context: " + context_id)
        username = "testuser"
        zap.users.new_user(context_id, username)
        userid = zap.users.users_list(context_id)[0]["id"]
        if cookie_name:
            zap.httpsessions.add_default_session_token(cookie_name)
            zap_access_target(zap, f"https://{domain}")
        # This is the secret sauce for using cookies.
        # The user above is now associated with the active cookie.
        # It should always choose the newest one.
        sessions = zap.httpsessions.sessions(site=domain+":443")
        session_name = sessions[-1]["session"][0]
        zap.users.set_authentication_credentials(context_id,
                                                    userid,
                                                    "sessionName=" + session_name)

        zap.users.set_user_enabled(context_id, userid, True)
        zap.forcedUser.set_forced_user(context_id, userid)
        zap.forcedUser.set_forced_user_mode_enabled(True)
        zap_access_target(zap, f"https://{domain}")
        return username, userid
    except Exception as e:
        logging.error("Cookie authentication setup failed.")
        raise RuntimeError("Failed to set the provided cookie" +
                           " as the default session in Zap.") from e


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
    logging.info("get_gcp_token fetching access token for the default identity")
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

def zap_set_iap_token(client_id):
    """
    Generate a Google id token for a oath client for the default identity.
    """
    logging.info("Fetching id token from google.")
    zap = zap_connect()
    open_id_connect_token = id_token.fetch_id_token( GoogleAuthRequest(),
                                                        client_id)
    bearer = f"Bearer {open_id_connect_token}"
    logging.info("zap replacer auth id token (IAP)")
    zap.replacer.add_rule(
        description="auth",
        enabled=True,
        matchtype="REQ_HEADER",
        matchregex=False,
        matchstring="Authorization",
        replacement=bearer
    )
    logging.info("zap replacer beehive")
    zap.replacer.add_rule(
        description="beehive",
        enabled=True,
        matchtype="REQ_HEADER",
        matchregex=False,
        matchstring="X-Beehive-Ignore-Github",
        replacement="True"
    )
    return open_id_connect_token


def zap_report(zap: ZAPv2, project: str, scan_type: ScanType, sites: str):
    """
    Generate ZAP scan XML report.
    """
    zap.core.set_option_merge_related_alerts(True)

    # This will export all findings independent of scope.
    # The more advanced zap report api calls require a directory local to zap
    # But you can download known files from /home/zap/.ZAP/transfer if you use an API key
    date = datetime.today()
    filename = f"{project}_{scan_type}-scan_report-{date.strftime('%Y-%m-%d')}.xml"
    filename = filename.replace("-", "_").replace(" ", "")

    template = "traditional-xml"
    report_dir = "/home/zap/.ZAP/transfer"
    # The sites parameter can take several urls separated with '|'.
    # Adding further sites to scope could be done by concatenating
    # them before passing them to this function.
    return_message = zap.reports.generate(title=project,
                                            reportfilename=filename,
                                            template=template,
                                            contexts=project,
                                            sites=sites,
                                            reportdir= report_dir)
    logging.info(return_message)
    # If successful we now have a report sitting in the transfer directory of the zap container
    report_data = zap.core.file_download(filename)
    with open(filename, "w") as report_file:
        report_file.write(report_data)
    return filename


def zap_save_session(zap: ZAPv2,
                     project: str,
                     scan_type: ScanType):
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
        shutil.make_archive(session_filename, 'zip', share_path_sess)
    except BaseException as base_error:  # pylint: disable=bare-except
        print("Unable to zip session file.")
        raise base_error
    return session_filename + ".zip"


def get_hail_token():
    """
    Fetches an openid token from google using a Service Account file.
    """
    credentials = os.getenv("HAIL_KEY")
    default_scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/appengine.admin',
            'https://www.googleapis.com/auth/compute',
            ]
    creds = json.loads(credentials)
    now = int(time.time())
    scope = ' '.join(default_scopes)
    print(creds['client_email'])
    assertion = {
        "aud": "https://www.googleapis.com/oauth2/v4/token",
        "iat": now,
        "scope": scope,
        "exp": now + 300,  # 5m
        "iss": creds['client_email'],
    }
    encoded_assertion = jwt.encode(assertion, creds['private_key'], algorithm='RS256')
    resp = requests.post('https://www.googleapis.com/oauth2/v4/token',
                                headers={'content-type': 'application/x-www-form-urlencoded'},
                                data=urlencode({
                                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                                    'assertion': encoded_assertion,
                                }
                            ))
    return resp.json()['access_token']

def zap_set_hail_token( zap, target_url):
    """
    Sets a google access token in ZAP for a dedicated service account for Hail.
    """
    token = get_hail_token()
    if token:
        bearer = f"Bearer {token}"
        zap.replacer.add_rule(
                        description="auth",
                        enabled=True,
                        matchtype="REQ_HEADER",
                        matchregex=False,
                        matchstring="Authorization",
                        replacement=bearer
                    )
    res = zap.urlopen(target_url)
    if res.split(':')[0] not in ("401","302"):
        return token
    raise RuntimeError("Failed to set token for hail.")


def zap_compliance_scan(
    project: str,
    target_url: str,
    scan_type: ScanType = ScanType.BASELINE,
):
    """
    Run a ZAP compliance scan of a given type against the target URL.
    """
    logging.info("=====  %s  %s  %s  =====", scan_type.name, project, target_url)

    host, _, path = parse_url(target_url)

    zap = zap_init(target_url)
    env = "prod"  # set prod as default
    if "dev" in host:
        env = "dev"
    # ZAP scans should be run in a context. This provides a scope for the scan,
    # and can provide more granular authentication controls.

    # Scan types:
    # BASELINE - unauthenticated, no active scan.
    # API - authenticated with SA, imports openid config, active scan is performed.
    # UI - authenticated with SA, active scan and ajax spider is performed.
    # AUTH - authenticated with SA, active scan is performed.
    # LEOAPP - authenticated with SA and registered cookie, active scan and ajax spider is performed
    # BEEHIVE - authenticated with iap bearer token and cookie.
    # IAPAUTH - authenticated with iap bearer token, api spec.
    # HAILAUTH - authenticated as a service account.

    # Set up context for scan
    context_id = zap_setup_context(zap, project, host)

    if scan_type != ScanType.BASELINE:
        if scan_type == ScanType.BEEHIVE or scan_type == ScanType.IAPAUTH:
            client_id = os.getenv('IAP_CLIENT_ID')
            token = zap_set_iap_token(client_id)
            if scan_type == ScanType.BEEHIVE:
                logging.info("Setting beehive session cookie.")
                cookie_name = "__host-beehive_session"
                zap_setup_cookie(zap, host, context_id, cookie_name)
        elif scan_type == ScanType.HAILAUTH or scan_type == ScanType.HAILAPI:
            token = zap_set_hail_token(zap, target_url)
        else:
            token = zap_sa_auth(zap, env)

        if scan_type == ScanType.LEOAPP:
            success = leo_auth(host, path, token)
            if success:
                # Sets a user in the context with the cookie,
                # and forces all Zap requests to use that cookie
                zap_setup_cookie(zap, host, context_id)
            else:
                logging.error("Leo authentication was unsuccessful")

    if scan_type == ScanType.API or scan_type == ScanType.HAILAPI:
        zap_api_import(zap, target_url)

    logging.info("zap spider scan %s", target_url)
    zap.spider.scan(contextname=project, url=target_url)

    if scan_type in (ScanType.UI, ScanType.LEOAPP, ScanType.BEEHIVE, ScanType.HAILAUTH):
        zap.ajaxSpider.scan(target_url, contextname=project)

    zap_wait_for_passive_scan(zap, timeout_in_secs=TIMEOUT_MINS * 60)

    if scan_type != ScanType.BASELINE:
        logging.info("zap ajax spider scan %s", target_url)
        zap.ascan.scan(target_url, contextid=context_id, recurse=True)

    logging.info("Scan complete. Cumulative alerts: %s", zap.alert.alerts_summary())
    filename = zap_report(zap, project, scan_type, f"https://{host}")
    session_file = zap_save_session(zap, project, scan_type)

    return (filename, session_file)
