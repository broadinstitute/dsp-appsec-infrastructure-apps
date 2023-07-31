"""
Provides methods for validating that an account is logged in,
and registered with Terra.
"""
import requests

# Library for ensuring the service account used for authentication is registered and logged in.

def terra_is_registered(token, env):
    """
    Checks if a user is registered with Terra.
    Will return True if registered, False if not.
    """
    is_registered = False
    url = ""
    if env.lower() == "dev":
        url = "https://sam.dsde-dev.broadinstitute.org/"
    else:
        url = "https://sam.dsde-prod.broadinstitute.org/"
    resp = requests.request(
        "GET",
        url + "register/user/v2/self/termsOfServiceComplianceStatus",
        timeout=5,
        headers={
            "Authorization": token
        })
    if resp.status_code == 200:
        is_registered = True
    return is_registered

def terra_register_sa(token, env):
    """
    Registers a user with Terra if they are not yet registered.
    Returns True if successfull, False if registration fails.
    """
    is_registered = False
    is_registered = terra_is_registered(token, env)
    url = ""
    # Usually dev URLs have "dev" in them.
    # This will only support dev and prod environments currently
    if env.lower() == "dev":
        url = "https://firecloud-orchestration.dsde-dev.broadinstitute.org/register/profile"
    else:
        url = "https://api.firecloud.org"
    if is_registered is False:
        # Login

        profile_json = {"firstName": "test",
                "lastName": "service account",
                "title": "None",
                "contactEmail": "",
                "institute": "None",
                "institutionalProgram": "None",
                "programLocationCity": "None",
                "programLocationState": "None",
                "programLocationCountry": "None",
                "pi": "None",
                "nonProfitStatus": "false"}
        resp = requests.request(
        "POST",
        url,
        timeout=5,
        headers={
            "Authorization": token,
            "Content-Type": "application/json"
        },
        data=profile_json)
        if resp.status_code == 200:
            is_registered = terra_is_registered(token, env)
    return is_registered


def terra_auth_logged_in(token, env):
    """
    Validates whether a user is logged into Terra.
    Equivalent to checking if bearer token is still valid.
    """
    logged_in = False
    url = ""
    if env.lower() == "dev":
        url = "https://sam.dsde-dev.broadinstitute.org/register/user/v2/self/info"
    else:
        url = "https://sam.dsde-prod.broadinstitute.org/register/user/v2/self/info"
    resp = requests.request(
        "GET",
        url,
        timeout=5,
        headers={
            "Authorization": token
        }
    )
    if resp.status == 200:
        logged_in = True

    return logged_in

def terra_tos(token, env):
    """
    Accepts the Terra TOS.
    There does not appear to be a problem with accepting it many times.
    """
    tos = False
    url = ""
    if env.lower() == "dev":
        url = "https://sam.dsde-dev.broadinstitute.org/register/user/v1/termsofservice"
    else:
        url = "https://sam.dsde-prod.broadinstitute.org/register/user/v1/termsofservice"

    resp = requests.request(
        "POST",
        url,
        timeout=5,
        headers={
            "Authorization": token,
            "Content-Type": "application/json"
        },
        data='"app.terra.bio/#terms-of-service"'
    )
    if resp.status_code == 200:
        tos = True
    return tos
