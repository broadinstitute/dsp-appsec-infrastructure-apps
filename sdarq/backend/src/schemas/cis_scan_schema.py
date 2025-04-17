cis_scan_schema = {
    "type": "object",
    "properties": {
        "project_id": {
            "type": "string",
            "pattern": "^[a-z0-9][a-z0-9-_]{4,42}[a-z0-9]$"
        },
        "results_in_slack": {
            "type": "array",
            "items": {
                "enum": ["Yes"]
            }
        },
        "slack_channel": {
            "type": "string",
            "pattern": "^[a-z0-9-_]{1}[a-z0-9-_]{0,40}$"
        }
    },
    "required": ["project_id"]
}
