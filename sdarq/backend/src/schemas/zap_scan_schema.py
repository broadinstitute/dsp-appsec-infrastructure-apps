zap_scan_schema = {
    "type": "object",
    "properties": {
        "URL": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "severities": {
            "type": "array",
            "items": {
                "enum": ["Critical", "High", "Medium", "Low", "Info"]
            }

        },
        "slack_channel": {
            "type": "string",
            "pattern": "^[a-z0-9-_]{1}[a-z0-9-_]{0,20}$"
        }
    },
    "required": ["URL", "severities", "slack_channel"]
}
