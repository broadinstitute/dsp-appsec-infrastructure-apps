edit_security_controls_schema = {
    "type": "object",
    "properties": {
        "product": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "security_champion": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-._\\s]{1,20}[a-zA-Z0-9]$"
        },
        "github": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "dev_url": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "defect_dojo": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "threat_model": {
            "type": "boolean",
        },
        "threat_model_link": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "zap": {
            "type": "boolean",
        },
        "vulnerability_management": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "sourceclear": {
            "type": "boolean",
        },
        "sourceclear_link": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
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
        "burp": {
            "type": "boolean",
        },
        "security_pentest_link": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        }
    },
    "required": ["product", "security_champion", "github", "dev_url"]
}
