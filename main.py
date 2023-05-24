"""Application endpoints"""
import os
from uuid import uuid4

import jinja2
from aioboto3 import Session
from aiofauna import FileField, Request
from botocore.config import Config
from dotenv import load_dotenv

from kubectl.client import client
from kubectl.config import DOCKER_URL, env
from kubectl.handlers import app, create_dns_record
from kubectl.models import Upload, User
from kubectl.utils import gen_port

load_dotenv()

#### Healthcheck Endpoint ####


@app.get("/")
async def healthcheck():
    """Healthcheck Endpoint"""
    return {"message": "Accepted", "status": "success"}


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


@app.post("/api/github/deploy/{owner}/{repo}")
async def deploy_container_from_repo(
    image: str, owner: str, repo: str, port: int = 8080, env_vars: str = "DOCKER=1"
):
    """Deploy a container from a github repo"""
    name = f"{owner}-{repo}-{str(uuid4())[:8]}"
    host_port = str(gen_port())
    payload = {
        "Image": image,
        "Env": env_vars.split(","),
        "ExposedPorts": {f"{str(port)}/tcp": {"HostPort": host_port}},
        "HostConfig": {"PortBindings": {f"{str(port)}/tcp": [{"HostPort": host_port}]}},
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
            name=name, port=port, host_port=host_port, ip=env.IP_ADDR
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
            "url": f"{name}.smartpro.solutions",
            "port": host_port,
            "container": data,
            "dns": res,
        }
    except KeyError:
        return container
