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
    cmd: L[str] = Field(["DOCKER=1"], description="Command to run")


class RepoDeployPayload(BaseModel):
    """
    
    Repository deploy payload
    
    """
    
    env_vars: O[L[str]] = Field(default=["DOCKER=1"], description="Environment variables")
    port:int=Field(default=8080, description="Port to expose")