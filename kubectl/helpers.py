import os

import jinja2

from .client import client
from .config import CLOUDFLARE_HEADERS, env

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))



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


async def provision_instance(name:str,port:int):
    dns_data = await create_dns_record(name)
    template = jinja_env.get_template("nginx.conf")
    nginx_config = template.render(name=name, port=port)
    for path in [
            "/etc/nginx/conf.d",
            "/etc/nginx/sites-available",
            "/etc/nginx/sites-enabled"
        ]:
            try:
                os.remove(f"{path}/{name}.conf")
            except: # pylint: disable=bare-except
                pass # pylint: disable=unnecessary-pass
            with open(f"{path}/{name}.conf", "w", encoding="utf-8") as f:
                f.write(nginx_config)
    os.system("nginx -s reload")
    return {
        "url": f"{name}.smartpro.solutions",
        "port": port,
        "dns": dns_data
    }