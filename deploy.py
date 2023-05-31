import os
import subprocess

import dotenv
import jinja2

env_loaded = dotenv.load_dotenv()
assert env_loaded is True

REGISTRY = os.getenv("REGISTRY")

def main():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    app = input("App name: ")
    assert isinstance(app, str)
    tag = input("Tag: ")
    if tag == "":
        tag = "latest"
    template = env.get_template("deploy.sh.j2")
    return template.render(app=app, tag=tag, registry=REGISTRY)

if __name__ == "__main__":
    script = main()
    with open("newdeploy.sh", "w") as f:
        f.write(script)
    subprocess.run(["chmod", "+x", "newdeploy.sh"])
    subprocess.run(["./newdeploy.sh"])
    os.remove("newdeploy.sh")

    print("Done!")
    