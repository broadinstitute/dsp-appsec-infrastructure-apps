new_service_schema = {
    "type": "object",
    "properties": {
        "Service": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "Product": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "Description": {
            "type": "string",
            "pattern": "[a-zA-Z0-9-_/ .?!]{4,200}"
        },
        "Security champion": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-._\\s]{1,20}[a-zA-Z0-9]$"
        },
        "Github URL": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "Architecture Diagram": {
            "type": "string",
            "pattern": "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"
        },
        "Compliance": {
            "type": "string",
            "pattern": "[a-zA-Z0-9-_,. ]{1,100}"
        },
        "JiraProject": {
            "type": "string",
            "pattern": "[a-zA-Z0-9-_]{1,7}"
        }
    },
    "required": ["Service", "Product", "Description", "Security champion", "Github URL", "Architecture Diagram", "Federal compliance oversight", "JiraProject"]
}
