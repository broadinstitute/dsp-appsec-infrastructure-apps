tm_schema = {
    "type": "object",
    "properties": {
        "Type": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9\\s]{1,30}[a-zA-Z0-9\s]$"
        },
        "Name": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,28}[a-zA-Z0-9]$"
        },
        "Github": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "Diagram": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "Document": {
            "type": "string",
            "pattern": "^(https?://)?[a-z0-9/\\./\\-]+(/[a-zA-Z0-9/\\-/\\/]*)?$"
        },
        "Eng": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-._\\s]{1,20}[a-zA-Z0-9]$"
        }
    },
    "required": ["Type", "Name", "Github", "Diagram", "Document", "Eng"]
}
