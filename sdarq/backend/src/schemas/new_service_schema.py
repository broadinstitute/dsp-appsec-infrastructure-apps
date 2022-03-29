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
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9,.!?-_\\s]{4,200}[a-zA-Z0-9,.!?-_\\s]$"
        },
        "Security champion": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-._\s]{4,20}[a-zA-Z0-9]$"
        },
        "Github URL": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "Architecture Diagram": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "Compliance": {
            "type": "string",
            "pattern": "[a-zA-Z0-9-_,. ]{1,100}"
        }
    },
    "required": ["Service", "Product", "Description", "Security champion", "Github URL", "Architecture Diagram", "Compliance"]
}
