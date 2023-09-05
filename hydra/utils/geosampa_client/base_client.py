import asyncio
import logging
import sys

import httpx
import requests
from requests.exceptions import RequestException
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from .decorators import json_response, raise_for_status, xml_response

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)


class BaseClient:
    """WFS base client - used to make generic requests"""

    accepted_versions = {"2.0.0"}
    output_formats = {"json", "xml", "bytes"}

    def __init__(self, domain: str, version: str = "2.0.0", verbose: bool = True):
        self.domain = self.__clean_domain(domain)
        self.version = self.__assert_version(version)
        self.host = self.__gen_host()
        self.verbose = verbose

    def __clean_domain(self, domain: str) -> str:
        if domain.endswith(r"/"):
            domain = domain[:-1]

        return domain

    def __assert_version(self, version: str) -> str:
        if version not in self.accepted_versions:
            raise ValueError(f"Accepted versions: {self.accepted_versions}")
        return version

    def __gen_host(self) -> str:
        wfs_version = f"/?service=WFS&version={self.version}"
        return self.domain + wfs_version

    def __solve_get_params(self, *ignore, **query_params: dict) -> str:
        request_args = ["=".join([param_name, str(param_value)]) for param_name, param_value in query_params.items()]
        query_string = "&".join(request_args)

        return query_string

    def __solve_req_capability(self, capability: str) -> str:
        capability_param = f"request={capability}"

        return capability_param

    def __solve_request_url(self, capability: str, **query_params: dict) -> str:
        base_url = self.host
        capability_param = self.__solve_req_capability(capability)
        url = base_url + "&" + capability_param

        if query_params is None:
            return url
        else:
            req_params = self.__solve_get_params(**query_params)
            return url + "&" + req_params

    @retry(
        retry=retry_if_exception_type(RequestException),
        stop=stop_after_attempt(10),
        wait=wait_random_exponential(5, min=5, max=60),
        before_sleep=before_sleep_log(logger, logging.INFO, exc_info=True),
    )
    @raise_for_status
    def wfs_generic_request(self, capability: str, *ignore, **query_params: dict) -> bytes:
        url = self.__solve_request_url(capability, **query_params)

        # response is in bytes, so must be decoed accordingly
        with requests.get(url) as response:
            return response

    async def wfs_async_requests(self, capability: str, pages, **query_params: dict):
        params = query_params.copy()
        async with httpx.AsyncClient() as client:

            @retry(
                retry=retry_if_exception_type(httpx.HTTPError),
                stop=stop_after_attempt(10),
                wait=wait_random_exponential(30, min=30, max=300),
                before_sleep=before_sleep_log(logger, logging.INFO, exc_info=True),
            )
            async def fetch(url, semaphore):
                async with semaphore:
                    response = await client.get(url, timeout=300)
                    response.raise_for_status()
                    return response

            tasks = []
            semaphore = asyncio.Semaphore(4)

            for page in pages:
                params["startIndex"] = page
                url = self.__solve_request_url(capability, **params)
                task = asyncio.create_task(fetch(url, semaphore))
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                # Handle exceptions
                print(f"Request failed: {response}")

        @json_response
        def parse_response(response):
            return response.content

        responses = [parse_response(response) for response in responses]

        first_response = responses[0]
        for response in responses[1:]:
            first_response["features"].extend(response["features"])

        return first_response

    @json_response
    def get_json(self, capability: str, **query_params: dict) -> dict:
        return self.wfs_generic_request(
            capability, outputFormat="application/json", exceptions="application/json", **query_params
        )

    @xml_response
    def get_xml(self, capability: str, **query_params: dict) -> dict:
        return self.wfs_generic_request(capability, **query_params)

    def __call__(self, capability: str, *ignore, output_format="json", pages=None, **query_params: dict) -> bytes:
        if output_format not in self.output_formats:
            raise ValueError(f"output_format must be in {self.output_formats}")

        if output_format == "json":
            return self.get_json(capability, **query_params)

        elif output_format == "xml":
            return self.get_xml(capability, **query_params)

        else:
            return self.wfs_generic_request(capability, **query_params)
