url_pattern = "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$|^$"

edit_security_controls_schema = {
    "type": "object",
    "properties": {
        "dev_url": {
            "type": "string",
            "pattern": url_pattern
        },
        "defect_dojo": {
            "type": "string",
            "pattern": url_pattern
        },
        "threat_model": {
            "type": "boolean",
        },
        "threat_model_link": {
            "type": "string",
            "pattern": url_pattern
        },
        "docker_scan": {
            "type": "boolean",
        },
        "cis_scanner": {
            "type": "boolean",
        },
        "burp": {
            "type": "boolean",
        },
        "security_pentest_link": {
            "type": "string",
            "pattern": url_pattern
        }
    }
}