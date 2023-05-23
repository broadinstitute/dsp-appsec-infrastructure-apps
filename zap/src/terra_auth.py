
import urllib3

# Library for ensuring the service account used for authentication is registered and logged in.

def terra_is_registered(token, env):
    is_registered = False
    url = ""
    if env.lower() == "dev":
        url = "https://sam.dsde-dev.broadinstitute.org/register/user/v2/self/termsOfServiceComplianceStatus"
    else:
        url = "https://sam.dsde-prod.broadinstitute.org/register/user/v2/self/termsOfServiceComplianceStatus"
    resp = urllib3.response(
        "GET",
        url,
        headers={
            "Authorization": token
        })
    if resp.status_code == 200:
        is_registered = True
    return is_registered

def terra_register_sa(token, env):
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
        resp = urllib3.response(
        "POST",
        url,
        headers={
            "Authorization": token,
            "Content-Type": "application/json"
        },
        data=profile_json)
        if resp.status_code == 200:
            is_registered = terra_is_registered(token, env)
    return is_registered
    

def terra_auth_logged_in(token, env):
    logged_in = False
    url = ""
    if env.lower() == "dev":
        url = "https://sam.dsde-dev.broadinstitute.org/register/user/v2/self/info"
    else:
        url = "https://sam.dsde-prod.broadinstitute.org/register/user/v2/self/info"
    resp = urllib3.response(
        "GET",
        url,
        headers={
            "Authorization": token
        }
    )
    if resp.status is 200:
        logged_in = True
    
    return logged_in

def terra_tos(token, env):
    tos = False
    url = ""
    if env.lower() == "dev":
        url = "https://sam.dsde-dev.broadinstitute.org/register/user/v1/termsofservice"
    else:
        url = "https://sam.dsde-prod.broadinstitute.org/register/user/v1/termsofservice"

    resp = urllib3.response(
        "POST",
        url,
        headers={
            "Authorization": token,
            "Content-Type": "application/json"
        },
        data="app.terra.bio/#terms-of-service"
    )
    if resp.status_code == 200:
        tos = True
    return tos
