zap_scan_schema = {
    "type": "object",
    "properties": {
        "URL": {
            "type": "string",
            "pattern": "^[a-z0-9][a-z0-9-_]{4,28}[a-z0-9]$"
        },
        "severities": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "[a-zA-Z]{10}"
            }

        },
        "slack_channel": {
            "type": "string",
            "pattern": "^[a-z0-9-_]{1}[a-z0-9-_]{0,20}$"
        }
    },
    "required": ["URL", "severities", "slack_channel"]
}
