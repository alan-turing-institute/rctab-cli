"""Types for the RCTab CLI.

Attributes:
    DATE_FORMATS: A list of date formats.
"""
from pydantic import AnyHttpUrl, BaseModel

DATE_FORMATS = ["%Y-%m-%d"]


class RCTabURL(BaseModel):
    """A URL endpoint for the RCTab API.

    Attributes:
        url: A URL endpoint.
    """

    url: AnyHttpUrl
