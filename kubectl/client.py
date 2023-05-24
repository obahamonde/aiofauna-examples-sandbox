"""
HTTP Client
"""

from typing import Any as A
from typing import AsyncGenerator as AG
from typing import Dict as D
from typing import Optional as O

from aiohttp import ClientSession


class APIClient:
    """

    Generic HTTP Client

    """

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: O[D[str, str]] = None,
        data: O[D[str, A]] = None,
    ) -> A:
        """
        Generic function to retrieve data from an URL in json format
        """
        if method in ["GET", "DELETE"]:
            async with ClientSession() as session:
                async with session.request(method, url, headers=headers) as response:
                    return await response.json()
        elif method in ["POST", "PUT", "PATCH"]:
            async with ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, json=data
                ) as response:
                    return await response.json()
        else:
            raise ValueError("Invalid method")

    async def text(
        self,
        url: str,
        method: str = "GET",
        headers: O[D[str, str]] = None,
        data: O[D[str, A]] = None,
    ) -> str:
        """
        Generic function to retrieve data from an URL in text format
        """
        if method in ["GET", "DELETE"]:
            async with ClientSession() as session:
                async with session.request(method, url, headers=headers) as response:
                    return await response.text()
        elif method in ["POST", "PUT", "PATCH"]:
            async with ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, json=data
                ) as response:
                    return await response.text()
        else:
            raise ValueError("Invalid method")

    async def blob(
        self,
        url: str,
        method: str = "GET",
        headers: O[D[str, str]] = None,
        data: O[D[str, A]] = None,
    ) -> bytes:
        """
        Generic function to retrieve data from an URL in binary format
        """
        if method in ["GET", "DELETE"]:
            async with ClientSession() as session:
                async with session.request(method, url, headers=headers) as response:
                    return await response.read()
        elif method in ["POST", "PUT", "PATCH"]:
            async with ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, json=data
                ) as response:
                    return await response.read()
        else:
            raise ValueError("Invalid method")

    async def stream(
        self,
        url: str,
        method: str = "GET",
        headers: O[D[str, str]] = None,
        data: O[D[str, A]] = None,
    ) -> AG[str, None]:
        """
        Generic function to retrieve data from an URL in streaming format
        """
        if method in ["GET", "DELETE"]:
            async with ClientSession() as session:
                async with session.request(method, url, headers=headers) as response:
                    async for chunk in response.content.iter_chunked(1024):
                        yield chunk.decode("utf-8")
        elif method in ["POST", "PUT", "PATCH"]:
            async with ClientSession() as session:
                async with session.request(
                    method, url, headers=headers, json=data
                ) as response:
                    async for chunk in response.content.iter_chunked(1024):
                        yield chunk.decode("utf-8")


client = APIClient()
