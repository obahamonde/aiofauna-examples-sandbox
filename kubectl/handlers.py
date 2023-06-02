"""Non decorated API Request Handlers"""
import asyncio
import json
import os

import jinja2
from aiofauna import Api, EventSourceResponse, FaunaClient, q
from aiohttp import ClientSession
from aiohttp.web import WebSocketResponse

from kubectl.client import client
from kubectl.config import CLOUDFLARE_HEADERS, DOCKER_URL, GITHUB_HEADERS, env
from kubectl.helpers import provision_instance
from kubectl.models import CodeServer, Container, DatabaseKey

app = Api()

@app.get("/api/docker/build/{owner}/{repo}")
async def docker_build_from_github_tarball(owner: str, repo: str):
    """
    Builds a Docker image from the latest code for the given GitHub repository.
    :param owner: The owner of the repository.
    :param repo: The name of the repository.
    :return: The output of the Docker build.
    """
    sha = await get_latest_commit_sha(owner, repo)
    tarball_url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{sha}"
    local_path = f"{owner}-{repo}-{sha[:7]}"
    build_args = json.dumps({"LOCAL_PATH": local_path})
    async with ClientSession() as session:
        async with session.post(
            f"{DOCKER_URL}/build?remote={tarball_url}&dockerfile={local_path}/Dockerfile&buildargs={build_args}"
        ) as response:
            streamed_data = await response.text()
            id_ = streamed_data.split("Successfully built ")[1].split("\\n")[0]
            return id_
    
@app.websocket("/api/docker/pull/{image}")
async def docker_pull(ws: WebSocketResponse, image: str):
    """
    Pulls a Docker image from Docker Hub.
    """
    async for event in client.stream(
        f"{DOCKER_URL}/images/create?fromImage={image}", "POST"
    ):
        await ws.send_json(json.loads(event))
        if "Pull complete" in event:
            await ws.send_json(event)
            return {"message": "Pull succeeded", "status": "success"}
    return {"message": "Pull failed", "status": "error"}



@app.get("/api/sha")
async def get_latest_commit_sha(owner: str, repo: str) -> str:
    """
    Gets the SHA of the latest commit in the repository.
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    payload = await client.fetch(url, headers=GITHUB_HEADERS)

    return payload[0]["sha"]


@app.get("/api/docker/start/{container}")
async def start_container(container: str):
    """Starts a docker container"""
    return await client.text(f"{DOCKER_URL}/containers/{container}/start", "POST")


@app.get("/api/codeserver")
async def get_code_server_image(ref:str):
    """
    Create a new CodeServer container
    """
    existing = await CodeServer.find_unique("user", ref) 
    
    if isinstance(existing, CodeServer):
        
        return {
            "instance": existing.dict(),
            "port": existing.port,
            "payload": existing.payload,
            "url": f"https://{ref}.smartpro.solutions"
        }
    
    instance = await CodeServer(user=ref).save()
    
    assert isinstance(instance, CodeServer)
    
    data = instance.payload
    
    data = await client.fetch(f"{DOCKER_URL}/containers/create", method="POST", data=data)

    _id = data["Id"]

    await client.text(f"{DOCKER_URL}/containers/{_id}/start", method="POST")
    
    container_info = await client.fetch(f"{DOCKER_URL}/containers/{_id}/json", method="GET")
    
    assert isinstance(instance.port,int)
    assert isinstance(instance.proxy_port,int)
    
    provision_info = await provision_instance(ref,instance.port)
    proxy_info = await provision_instance(f"{ref}-proxy",instance.proxy_port)
    
    
    
    return {
        "container": _id,
        "port": instance.port,
        "url": f"https://{ref}.smartpro.solutions",
        "proxy": f"https://{ref}-proxy.smartpro.solutions",
        "provision_info": provision_info,
        "proxy_provision": proxy_info,
        "info": container_info
    }
    
    
        
@app.get("/api/db/{ref}")
async def get_database_key(ref:str):
    """Get the database key"""
    try:
        instance = await DatabaseKey.find_unique("user", ref)
        if isinstance(instance, DatabaseKey):
            return instance
        fql = FaunaClient(secret=env.FAUNA_SECRET)
        # Create a new database
        database = await fql.query(q.create_database({"name": ref}))
        global_id = database["global_id"]
        db_ref = database["ref"]["@ref"]["id"]
        # Create a new key
        key = await fql.query(q.create_key({"database": q.database(db_ref), "role": "admin"}))
        key_ref = key["ref"]["@ref"]["id"]
        secret = key["secret"]
        hashed_secret = key["hashed_secret"]
        role = key["role"]
        
        return await DatabaseKey(
            user=ref,
            database=db_ref,
            global_id=global_id,
            key=key_ref,
            secret=secret,
            hashed_secret=hashed_secret,
            role=role
        ).save()
    except Exception as e:
        

        return {"message": str(e), "status": "error"}