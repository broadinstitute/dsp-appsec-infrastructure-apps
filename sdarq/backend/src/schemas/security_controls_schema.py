security_controls_schema = {
    "type": "object",
    "properties": {
        "product": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "service": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "security_champion": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-._\s]{4,20}[a-zA-Z0-9]$"
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
            "type": "string",
            "pattern": "[a-zA-Z]{5}"
        },
        "threat_model_link": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "zap": {
            "type": "string",
            "pattern": "[a-zA-Z]{5}"
        },
        "vulnerability_management": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "sourceclear": {
            "type": "string",
            "pattern": "[a-zA-Z]{5}"
        },
        "sourceclear_link": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "docker_scan": {
            "type": "string",
            "pattern": "[a-zA-Z]{5}"
        },
        "cis_scanner": {
            "type": "string",
            "pattern": "[a-zA-Z]{5}"
        },
        "sast": {
            "type": "string",
            "pattern": "[a-zA-Z]{5}"
        },
        "burp": {
            "type": "string",
            "pattern": "[a-zA-Z]{5}"
        },
        "security_pentest_link": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        }
    },
    "required": ["product", "service", "security_champion", "github"]
}
