url_pattern = "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"

new_app_schema = {
    "type": "object",
    "properties": {
        "Service": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,40}[a-zA-Z0-9]$"
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
            "pattern": "^(https://github.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+|(N/A))$"
        },
        "Architecture Diagram": {
            "type": "string",
            "pattern": url_pattern
        },
        "JiraProject": {
            "type": "string",
            "pattern": "([A-Z][A-Z0-9]+)"
        }
    },
    "required": ["Service", "Description", "Security champion", "Github URL", "Architecture Diagram", "JiraProject"]
}
