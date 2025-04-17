zap_scan_schema = {
    "type": "object",
    "properties": {
        "URL": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "slack_channel": {
            "type": "string",
            "pattern": "^[a-z0-9-_]{1}[a-z0-9-_]{0,40}$"
        }
    },
    "required": ["URL", "slack_channel"]
}
