"""

AioFauna Models

"""
from datetime import datetime
from typing import List as L
from typing import Optional as O

from aioboto3 import Session
from aiofauna import FaunaModel as Q
from aiofauna import Field

from kubectl.utils import gen_port

session = Session()


class Upload(Q):
    """

    R2 Upload Record

    """

    user: str = Field(..., description="User sub", index=True)
    name: str = Field(..., description="File name")
    key: str = Field(..., description="File key", unique=True)
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

    sub: str = Field(..., unique=True)
    name: str = Field(...)
    email: O[str] = Field(None, index=True)
    picture: O[str] = Field(None)
    nickname: O[str] = Field(None)
    given_name: O[str] = Field(None)
    family_name: O[str] = Field(None)
    locale: O[str] = Field(None, index=True)
    updated_at: O[str] = Field(None)
    email_verified: O[bool] = Field(None, index=True)


class DatabaseKey(Q):
    """

    Fauna Database Key

    """

    user:str = Field(..., unique=True)
    database: str = Field(...)
    global_id: str = Field(...)
    key: str = Field(...)
    secret: str = Field(...)
    hashed_secret: str = Field(...)
    role: str = Field(...)
    
    
class CodeServer(Q):
    """

    Code server payload

    """

    user: str = Field(..., description="User reference", unique=True)
    image: O[str] = Field(default="linuxserver/code-server", description="Image to use")
    port: O[int] = Field(default_factory=gen_port, description="Port to expose")
    env_vars: O[L[str]] = Field(default=[], description="Environment variables")
    
    @property
    def payload(self):
        """

        Payload

        """
        assert isinstance(self.env_vars, list)
        self.env_vars.append(f"PASSWORD={self.user}")
        self.env_vars.append("TZ=America/New_York")
        self.env_vars.append(f"PUID={self.user}")
        self.env_vars.append(f"PGID={self.user}")
        self.env_vars.append(f"USER={self.user}")
        self.env_vars.append(f"PROXY_DOMAIN={self.user}.smartpro.solutions")
        self.env_vars.append(f"SUDO_PASSWORD={self.user}")
        
        return {
            "Image": self.image,
            "Env": self.env_vars,
            "ExposedPorts": {"8443/tcp": {"HostPort": str(self.port)}},
            "HostConfig": {
                "PortBindings": {"8443/tcp": [{"HostPort": str(self.port)}]}
            },
        }
