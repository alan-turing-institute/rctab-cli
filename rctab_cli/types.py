"""Types for the RCTab CLI."""
from pydantic import AnyHttpUrl, BaseModel


class RCTabURL(BaseModel):
    """A URL endpoint for the RCTab API.

    Attributes:
        url: A URL endpoint.
    """

    url: AnyHttpUrl
