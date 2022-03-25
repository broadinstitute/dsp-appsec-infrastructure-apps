cis_scan_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-z0-9][a-z0-9-_]{4,28}[a-z0-9]$"
        },
        "results_in_slack": {
            "type": "string",
            "pattern": "[a-zA-Z]{3}"
        },
        "slack_channel": {
            "type": "string",
            "pattern": "^[a-z0-9-_]{1}[a-z0-9-_]{0,20}$"
        }
    },
    "required": ["name"]
}
