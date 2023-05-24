"""

Request Payloads

"""

from typing import List as L  # pylint: disable=unused-import
from typing import Optional as O

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from kubectl.utils import gen_oid, gen_port


class RepoBuildPayload(BaseModel):
    """

    Repository build payload

    """

    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    port: O[int] = Field(default_factory=gen_port, description="Port to expose")
    env_vars: L[str] = Field([], description="Environment variables")
    cmd: L[str] = Field([], description="Command to run")


class CodeServerPayload(BaseModel):
    """

    Code server payload

    """

    ref: str = Field(..., description="User reference")
    image: O[str] = Field(default="linuxserver/code-server", description="Image to use")
    port: O[int] = Field(default_factory=gen_port, description="Port to expose")
    env_vars: O[L[str]] = Field(default=[], description="Environment variables")

    @property
    def payload(self):
        """

        Payload

        """
        assert isinstance(self.env_vars, list)
        self.env_vars.append(f"PASSWORD={self.ref}")
        self.env_vars.append("TZ=America/New_York")
        self.env_vars.append(f"PUID={self.ref}")
        self.env_vars.append(f"PGID={self.ref}")
        self.env_vars.append(f"USER={self.ref}")
        self.env_vars.append(f"PROXY_DOMAIN={self.ref}.smartpro.solutions")

        return {
            "Image": self.image,
            "Env": self.env_vars,
            "ExposedPorts": {"8443/tcp": {"HostPort": str(self.port)}},
            "HostConfig": {
                "PortBindings": {"8443/tcp": [{"HostPort": str(self.port)}]}
            },
        }
