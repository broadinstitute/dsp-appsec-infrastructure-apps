url_pattern = "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"

edit_security_controls_schema = {
    "type": "object",
    "properties": {
        "product": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "github": {
            "type": "string",
            "pattern": url_pattern
        },
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
        "zap": {
            "type": "boolean",
        },
        "vulnerability_management": {
            "type": "string",
            "pattern": url_pattern
        },
        "sourceclear": {
            "type": "boolean",
        },
        "sourceclear_link": {
            "type": "string",
            "pattern": url_pattern
        },
        "docker_scan": {
            "type": "boolean",
        },
        "cis_scanner": {
            "type": "boolean",
        },
        "sast": {
            "type": "boolean",
        },
        "sast_link": {
            "type": "string",
            "pattern": url_pattern
        },
        "burp": {
            "type": "boolean",
        },
        "security_pentest_link": {
            "type": "string",
            "pattern": url_pattern
        }
    },
    "required": ["product", "github", "dev_url"]
}