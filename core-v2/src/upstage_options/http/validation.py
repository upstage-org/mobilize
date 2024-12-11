from typing import Optional
from pydantic import BaseModel, Field


class ConfigInput(BaseModel):
    name: str = Field(..., description="The name of the configuration")
    value: str = Field(..., description="The value of the configuration")


class SystemEmailInput(BaseModel):
    subject: str = Field(..., description="The subject of the email")
    body: str = Field(..., description="The body of the email")
    recipients: str = Field(..., description="The recipient of the email")
    bcc: Optional[str] = Field(None, description="The BCC recipients of the email")
