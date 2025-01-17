"""
Provides the ScanType Enum.
"""

from enum import Enum


class ScanType(str, Enum):
    """
    Enumerates Zap compliance scan types
    """

    API = "API"
    AUTH = "Authenticated"
    BASELINE = "Baseline"
    UI = "UI"
    LEOAPP = "LeoApp"
    BEEHIVE = "beehive"
    IAPAUTH ="IAPAUTH"
    HAILAUTH = "HAILAUTH"
    HAILAPI = "HAILAPI"

    def __str__(self):
        return str(self.name).lower()

    def label(self):
        """"Get user-friendly name of the scan type"""
        return str(self.value)
        