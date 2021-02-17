import argparse
import re
from typing import List, Literal, Optional, Set, TypedDict
from enum import Enum


class Endpoint(TypedDict):
    """
    Defines she shape of an Endpoint object returned from DefectDojo.
    """

    protocol: Literal["http", "https"]
    host: str
    port: Optional[int]
    path: Optional[str]
    tags: List[str]


class ScanType(str, Enum):
    """
    Enumerates Zap compliance scan types
    """

    API = "API"
    AUTH = "Authenticated"
    BASELINE = "Baseline"
    UI = "UI"

    def __str__(self):
        return str(self.name).lower()

    def label(self):
        """"Get user-friendly name of the scan type"""
        return str(self.value)


TAG_MATCHER = re.compile(r"^([^:]+):(.*)$")


def parse_tags(endpoint: Endpoint):
    """
    Parse tags for a given endpoint.
    """
    codedx_project = ""
    slack_channel = ""
    scan_type: Optional[ScanType] = None
    for tag in endpoint["tags"]:
        tag_match = TAG_MATCHER.match(tag)
        if not tag_match:
            continue

        tag_key, tag_val = tag_match.group(1), tag_match.group(2)
        if tag_key == "codedx":
            codedx_project = tag_val
        if tag_key == "scan":
            scan_type = ScanType[tag_val.upper()]
    return codedx_project, scan_type.name
