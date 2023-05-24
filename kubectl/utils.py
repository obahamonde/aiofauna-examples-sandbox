"""Utility functions for the API."""
import os
import socket
from datetime import datetime
from random import choice, randint
from secrets import token_urlsafe
from uuid import uuid4


def get_dir_size(path="."):
    """Get the size of a directory in bytes."""
    total = 0
    with os.scandir(path) as it_:
        for entry in it_:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total


def build_file_tree(root_dir):
    """Build a file tree from a given directory."""
    file_tree = {
        "name": os.path.basename(root_dir),
        "type": "directory",
        "children": [],
    }

    for file_name in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file_name)

        if os.path.isdir(file_path):
            file_tree["children"].append(build_file_tree(file_path))
        else:
            try:
                with open(file_path, "r", encoding="utf-8") as file_:
                    file_content = file_.read()
            except:
                file_content = "[BINARY]"

            file_tree["children"].append(
                {"name": file_name, "type": "file", "content": file_content}
            )

    return file_tree


def gen_oid():
    """Generate a unique object id."""
    return str(uuid4())


def gen_now():
    """Generate a timestamp."""
    return datetime.now().isoformat()


def gen_ip():
    """Generate a random ip address."""
    return ".".join([str(randint(0, 255)) for _ in range(4)])


def gen_password():
    """Generate a random password."""
    return "".join(
        [
            choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)")
            for _ in range(randint(8, 16))
        ]
    )


def gen_secret():
    """Generate a random secret."""
    return token_urlsafe(32)


def gen_port():
    """Generate a random port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
