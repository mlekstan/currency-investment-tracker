from dataclasses import dataclass
from typing import Literal, NotRequired, Optional, TypedDict

import requests


class HttpException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)


class MakeRequestOptions(TypedDict): 
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    headers: NotRequired[dict[str, str]]
    body: NotRequired[any]


@dataclass
class HttpApiClientConfig:
    scheme: Literal["http", "https"]
    host: str
    port: Optional[int] = None


class HttpApiClient:
    def __init__(self, config: HttpApiClientConfig):
        self.config = config
        self._schemePort = {"http": 80, "https": 443}

    def make_request(self, path: str, options: MakeRequestOptions) -> requests.Response:
        method = options.get("method")
        headers = options.get("headers", None)
        body = options.get("body", None)

        port = self.config.port or self._schemePort[self.config.scheme]
        baseUrl = f"{self.config.scheme}://{self.config.host}:{port}"
        fullUrl = f"{baseUrl}/{path.lstrip('/')}"

        print("Full path", fullUrl)

        response = requests.request(
            method=method,
            url=fullUrl,
            headers=headers, 
            data=body
        )

        if not response.ok:
            raise HttpException(response.status_code, response.text)

        return response