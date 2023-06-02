"""

AioFauna Models

"""
import os
from datetime import datetime
from random import randint
from typing import List as L
from typing import Optional as O

import jinja2
from aioboto3 import Session
from aiofauna import FaunaModel as Q
from aiofauna import Field
from names import get_full_name
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from kubectl.helpers import jinja_env
from kubectl.payload import RepoDeployPayload
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
    content_type: str = Field(..., description="File type", index=True)
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
    container_id: O[str] = Field(default=None, unique=True)
    user: str = Field(..., description="User reference", unique=True)
    image: O[str] = Field(default="linuxserver/code-server", description="Image to use")
    port: O[int] = Field(default_factory=gen_port, description="Port to expose")
    proxy_port: O[int] = Field(default_factory=gen_port, description="Proxy port")
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
        
        os.makedirs(f"./.vscode/{self.user}/config/workspace", exist_ok=True)
        os.makedirs(f"./.vscode/{self.user}/config/extensions", exist_ok=True)        
        
        code_server_settings = jinja_env.get_template("settings.json").render()
        
        with open(f"./.vscode/{self.user}/config/extensions/settings.json", "w") as f:
            f.write(code_server_settings)
        
        return {
            "Image": self.image,
            "Env": self.env_vars,
            "ExposedPorts": {"8443/tcp": {"HostPort": str(self.port)}},
            "HostConfig": {
                "PortBindings": {"8443/tcp": [{"HostPort": str(self.port)}],
                                 "8080/tcp": [{"HostPort": str(self.proxy_port)}]},
            },
            "Volumes": {f"./.vscode/{self.user}/config/workspace": {
                "bind": "/config/workspace",
                "mode": "rw"
            },
            f"./.vscode/{self.user}/config/extensions": {
                "bind": "/config/extensions",
                "mode": "rw"
            }
        }
        }



class MetricsSchema(BaseModel):
    """The schema of the metrics."""

    latency: float = Field(
        ..., description="The time taken for the request to be processed by the server."
    )
    cpu_cycle: int = Field(
        ...,
        description="The number of CPU cycles taken for the request to be processed by the server.",
    )
    memory: int = Field(
        ...,
        description="The amount of memory taken for the request to be processed by the server.",
    )
    network_time: float = Field(
        ..., description="The time taken for the request to be processed by the server."
    )
    network_speed: float = Field(..., description="The network speed of the server.")
    requests_per_second: float = Field(
        ..., description="The number of requests processed by the server per second."
    )


class MetricsModel(Q):
    """The metrics stored in the database."""

    metrics: MetricsSchema = Field(..., description="The schema of the metrics.")
    endpoint: str = Field(..., description="The endpoint of the metrics.")
    method: str = Field(..., description="The method of the metrics.")
    timestamp: float = Field(
        default_factory=datetime.now().timestamp,description="The timestamp of the metrics."
    )
    
class Container(Q):
    owner: str = Field(..., description="User reference", index=True)
    repo: str = Field(..., description="Repo reference", index=True)
    name:str = Field(..., unique=True)
    user: str = Field(..., description="User reference", index=True)
    url: O[str] = Field(None, description="Container url")
    data: O[dict] = Field(None, description="Container data")
    repo_payload: O[RepoDeployPayload] = Field(None, description="Repo payload")
    