edit_security_controls_schema = {
    "type": "object",
    "properties": {
        "product": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "github": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "dev_url": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "defect_dojo": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "threat_model": {
            "type": "boolean",
        },
        "threat_model_link": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "zap": {
            "type": "boolean",
        },
        "vulnerability_management": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "sourceclear": {
            "type": "boolean",
        },
        "sourceclear_link": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
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
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "burp": {
            "type": "boolean",
        },
        "security_pentest_link": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        }
    },
    "required": ["product", "github", "dev_url"]
}
