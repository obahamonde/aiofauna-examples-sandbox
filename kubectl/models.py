"""

AioFauna Models

"""
from datetime import datetime
from typing import Optional as O

from aioboto3 import Session
from aiofauna import FaunaModel as Q
from aiofauna import Field

session = Session()


class Upload(Q):
    """

    R2 Upload Record

    """

    user: str = Field(..., description="User sub", index=True)
    name: str = Field(..., description="File name")
    key: str = Field(..., description="File key")
    size: int = Field(..., description="File size", gt=0)
    type: str = Field(..., description="File type", index=True)
    lastModified: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        description="Last modified",
        index=True,
    )
    url: O[str] = Field(None, description="File url")


class User(Q):
    """

    Auth0 User

    """

    sub: str = Field(..., index=True)
    name: str = Field(...)
    email: O[str] = Field(None, index=True)
    picture: O[str] = Field(None)
    nickname: O[str] = Field(None)
    given_name: O[str] = Field(None)
    family_name: O[str] = Field(None)
    locale: O[str] = Field(None, index=True)
    updated_at: O[str] = Field(None)
    email_verified: O[bool] = Field(None, index=True)
