"""Non decorated API Request Handlers"""
import json
import os

import jinja2
from aiofauna import Api, EventSourceResponse

from kubectl.client import client
from kubectl.config import CLOUDFLARE_HEADERS, DOCKER_URL, GITHUB_HEADERS, env
from kubectl.payload import CodeServerPayload

app = Api()


@app.sse("/api/docker/build/{owner}/{repo}")
async def docker_build_from_github_tarball(
    sse: EventSourceResponse, owner: str, repo: str
):
    """
    Builds a Docker image from the latest code for the given GitHub repository.
    """
    sha = await get_latest_commit_sha(owner, repo)
    tarball_url = f"https://api.github.com/repos/{owner}/{repo}/tarball"
    local_path = f"{owner}-{repo}-{sha[:7]}"
    build_args = json.dumps({"LOCAL_PATH": local_path})
    async for chunk in client.stream(
        f"{DOCKER_URL}/build?buildargs={build_args}&remote={tarball_url}",
        "POST",
        headers={"Content-Type": "application/tar"},
    ):
        await sse.send(chunk)
        if "Successfully built" in chunk:
            await sse.send(chunk)
            id_ = chunk.split("Successfully built ")[1].split("\\n")[0]
            return {"message": "Build succeeded", "status": "success", "id": id_}
    return {"message": "Build failed", "status": "error"}


@app.sse("/api/docker/pull")
async def docker_pull(sse: EventSourceResponse, image: str):
    """
    Pulls a Docker image from Docker Hub.
    """
    async for event in client.stream(
        f"{DOCKER_URL}/images/create?fromImage={image}", "POST"
    ):
        await sse.send(event)
        if "Pull complete" in event:
            await sse.send(event)
            break
    return sse


@app.get("/api/dns/records")
async def create_dns_record(name: str):
    """Create an A record for a given subdomain"""
    payload = {
        "type": "A",
        "name": name,
        "content": env.IP_ADDR,
        "ttl": 1,
        "proxied": True,
    }

    return await client.fetch(
        f"https://api.cloudflare.com/client/v4/zones/{env.CF_ZONE_ID}/dns_records",
        "POST",
        headers=CLOUDFLARE_HEADERS,
        data=payload,
    )

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


@app.get("/api/docker/codeserver")
async def get_code_server_image(ref:str):
    """
    Gets the SHA of the latest commit in the repository.
    """
    payload = CodeServerPayload(ref=ref)
    
    data = payload.payload
    
    data = await client.fetch(f"{DOCKER_URL}/containers/create", method="POST", data=data)

    _id = data["Id"]
    
    try:
        
        await start_container(_id)
        res = await create_dns_record(ref)
        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
        template = jinja_env.get_template("nginx.conf")
        nginx_config = template.render(name=ref, port=payload.port)
        for path in [
            "/etc/nginx/conf.d",
            "/etc/nginx/sites-enabled",
            "/etc/nginx/sites-available",
        ]:
            try:
                os.remove(f"{path}/{ref}.conf")
            except: # pylint: disable=bare-except
                pass # pylint: disable=unnecessary-pass
            with open(f"{path}/{ref}.conf", "w", encoding="utf-8") as f:
                f.write(nginx_config)
        os.system("nginx -s reload")
        this = await client.fetch(f"{DOCKER_URL}/containers/{_id}/json")
        return {
            "url": f"{ref}.smartpro.solutions",
            "port": payload.port,
            "container": this,
            "dns": res,
        }
    except KeyError:
        return data 