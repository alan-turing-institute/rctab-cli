from pydantic import AnyHttpUrl, BaseModel

DATE_FORMATS = ["%Y-%m-%d"]


class RCTabURL(BaseModel):
    url: AnyHttpUrl
