url_pattern = "^((http|https)://)[-a-zA-Z0-9@:%._\\+~#?&//=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%._\\+~#?&//=]*)$"

tm_schema = {
    "type": "object",
    "properties": {
        "Type": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9 ]{1,30}[a-zA-Z0-9 ]$"
        },
        "Name": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9][a-zA-Z0-9-_ ]{1,40}[a-zA-Z0-9]$"
        },
        "Github": {
            "type": "string",
            "pattern": url_pattern
        },
        "Diagram": {
            "type": "string",
            "pattern": url_pattern
        },
        "Document": {
            "type": "string",
            "pattern": url_pattern
        }
    },
    "required": ["Type", "Name", "Github", "Diagram", "Document"]
}
