"""Application endpoints"""
import asyncio
import os
from uuid import uuid4

import jinja2
from aioboto3 import Session
from aiofauna import (FaunaModel, FileField, Request,  # pylint: disable=all
                      render_template)
from botocore.config import Config
from dotenv import load_dotenv

from kubectl.client import client
from kubectl.config import DOCKER_URL, env
from kubectl.handlers import (app, create_dns_record,
                              docker_build_from_github_tarball,
                              start_container)
from kubectl.models import Upload, User
from kubectl.payload import RepoDeployPayload
from kubectl.utils import gen_port

load_dotenv()

#### Healthcheck Endpoint ####


#### Authorizer ####


@app.get("/api/auth")
async def authorize(token: str):
    """Authorization Endpoint, exchange token for user info"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{env.AUTH0_DOMAIN}/userinfo"
    user_dict = await client.fetch(url, headers=headers)
    return await User(**user_dict).save()


#### Bucket obj Endpoints ####

session = Session()


@app.delete("/api/upload")
async def delete_upload(ref: str):
    """Delete an uploaded file given it's document reference"""
    await Upload.delete(ref)
    return {"message": "Asset deleted successfully", "status": "success"}


@app.get("/api/upload")
async def get_upload(user: str):
    """Fetch Uploaded files for a given user"""
    return await Upload.find_many("user", user)


@app.post("/api/upload")
async def upload_handler(request: Request):
    """Upload a file to the bucket"""
    data = await request.post()
    params = dict(request.query)
    key = params.get("key")
    size = params.get("size")
    user = params.get("user")
    if key and size and user:
        size = int(size)
        file = data["file"]
        if isinstance(file, FileField):
            async with session.client(
                service_name="s3",
                aws_access_key_id=env.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
                endpoint_url=env.AWS_S3_ENDPOINT,
                config=Config(signature_version="s3v4"),
            ) as s3client:  # type: ignore
                key_ = f"{key}/{file.filename}"  # type: ignore
                await s3client.put_object(
                    Bucket=env.AWS_S3_BUCKET,
                    Key=key_,
                    Body=file.file.read(),
                    ContentType=file.content_type,
                    ACL="public-read",
                )
                url = await s3client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": env.AWS_S3_BUCKET, "Key": key_},
                    ExpiresIn=3600 * 7 * 24,
                )
                return await Upload(
                    user=user,
                    key=key_,
                    name=file.filename,
                    size=size,
                    type=file.content_type,
                    url=url,
                ).save()
    return {"message": "Invalid request", "status": "error"}

async def container_exists(id:str)->bool:
    """Check if a container exists"""
    try:
        await client.fetch(f"{DOCKER_URL}/containers/{id}/json")
        return True
    except Exception as e:
        return False

async def delete_container(id:str):
    """Delete a container"""
    try:
        await client.fetch(f"{DOCKER_URL}/containers/{id}",method="DELETE")
    except Exception as e:
        print(e)


@app.post("/api/deploy/{owner}/{repo}")
async def deploy_container_from_repo(owner:str,repo:str,body:RepoDeployPayload
):
    """Deploy a container from a github repo"""
    sha = uuid4().hex[:7]
    name = f"{owner}-{repo}-{sha}"
    if await container_exists(name):
        await delete_container(name)
    else:
        print("Container does not exist")
    host_port = str(gen_port())
    image = await docker_build_from_github_tarball(owner, repo)
    if image is None:
        return {
            "message": "Failed to build image",
            "status": "error"
        }
 
    payload = {
        "Image": image,
        "Env": body.env_vars,
        "ExposedPorts": {f"{str(body.port)}/tcp": {"HostPort": host_port}},
        "HostConfig": {"PortBindings": {f"{str(body.port)}/tcp": [{"HostPort": host_port}]}},
    }
    container = await client.fetch(
        f"{DOCKER_URL}/containers/create?name={name}",
        "POST",
        headers={"Content-Type": "application/json"},
        data=payload,
    )
    try:
        _id = container["Id"]
        await start_container(_id)
        res = await create_dns_record(name)
        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
        template = jinja_env.get_template("nginx.conf")
        nginx_config = template.render(
            name=name, port=host_port
        )
        for path in [
            "/etc/nginx/conf.d",
            "/etc/nginx/sites-enabled",
            "/etc/nginx/sites-available",
        ]:
            try:
                os.remove(f"{path}/{name}.conf")
            except:  # pylint: disable=bare-except
                pass  # pylint: disable=unnecessary-pass
            with open(f"{path}/{name}.conf", "w", encoding="utf-8") as f:
                f.write(nginx_config)
        os.system("nginx -s reload")
        data = await client.fetch(f"{DOCKER_URL}/containers/{_id}/json")
        return {
            "url": f"https://{name}.smartpro.solutions",
            "port": host_port,
            "container": data,
            "dns": res,
            "image": image,
        }
    except KeyError:
        return container


import inspect

import kubectl.models as models

models_ = [n for m,n in inspect.getmembers(models) if inspect.isclass(n) and issubclass(n, FaunaModel) and n != FaunaModel]

@app.get("/")
async def index():
    return render_template("index.html")

#@app.on_event("startup")
async def startup(_):
    await asyncio.gather(*[m.provision() for m in models_])

if __name__ == "__main__":
    app.run(port=8080,host="0.0.0.0")