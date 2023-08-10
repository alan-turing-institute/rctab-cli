"""Types for the rctab CLI.

Attributes:
    DATE_FORMATS: A list of date formats.
"""
from pydantic import AnyHttpUrl, BaseModel

DATE_FORMATS = ["%Y-%m-%d"]


class RCTabURL(BaseModel):
    """A url endpoint for the rctab API.
    
    Attributes:
        url: A url endpoint.
    """
    url: AnyHttpUrl
