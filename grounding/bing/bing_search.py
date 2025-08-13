# https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/bing-code-samples?pivots=rest
# https://learn.microsoft.com/en-us/rest/api/aifoundry/aiagents/operation-groups?view=rest-aifoundry-aiagents-v1

import asyncio
import json
import time
from datetime import datetime, timedelta
from functools import wraps

import aiohttp
from azure.core.credentials import TokenCredential
from pydantic import BaseModel, Field


class GroundingWithBingSearch:

    def __init__(self, endpoint: str, credential: TokenCredential, api_version:str, connection_id: str, **kwargs) -> None:
        """
        Initialize Bing Search API client

        Args:
            endpoint: Azure OpenAI endpoint
            credential: Authentication info (TokenCredential)
            **kwargs: Additional arguments
        """
        self.endpoint = endpoint
        self.api_version = api_version
        self.credential = credential
        self.connection_id = connection_id
        self.kwargs = kwargs
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_token().token}"
        }
        self.agent_id = None
        self.thread_id = None

        # print(f"BingSearch initialized with endpoint: {self.endpoint}, api_version: {self.api_version}, connection_id: {self.connection_id}")

    # region Decorators
    def measure_time_async(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            end = time.perf_counter()
            print(f"{func.__name__} elapsed: {end - start:.4f}s")
            return result
        return wrapper
    # endregion

    # region Private methods
    def _get_token(self):
        scope = "https://ai.azure.com/.default"
        return self.credential.get_token(scope)

    async def _post(self, url: str, data: str = None):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, data=data) as response:
                result = await response.json()
                return result
    async def _get(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                result = await response.json()
                return result
    async def _delete(self, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self.headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to delete: {response.status}")
                return None

    @measure_time_async
    async def _create_agent(self):
        url = f"{self.endpoint}/assistants?api-version={self.api_version}"
        payload = CreateAgentRequest()
        payload.tools[0].bing_grounding.search_configurations[0].connection_id = self.connection_id
        return await self._post(url, payload.serialize())

    async def _delete_agent(self, agent_id: str):
        url = f"{self.endpoint}/assistants/{agent_id}?api-version={self.api_version}"
        await self._delete(url)

    @measure_time_async
    async def _create_thread(self):
        url = f"{self.endpoint}/threads?api-version={self.api_version}"
        return await self._post(url, data='')

    async def _delete_thread(self, thread_id: str):
        url = f"{self.endpoint}/threads/{thread_id}?api-version={self.api_version}"
        await self._delete(url)

    @measure_time_async
    async def _ask_to_thread(self, thread_id: str, message: str):
        url = f"{self.endpoint}/threads/{thread_id}/messages?api-version={self.api_version}"

        payload = {
            "content": message,
            "role": "user"
        }
        return await self._post(url, json.dumps(payload))

    @measure_time_async
    async def _runs(self, thread_id: str, assistant_id: str):
        url = f"{self.endpoint}/threads/{thread_id}/runs?api-version={self.api_version}"

        payload = {
            "assistant_id": assistant_id
        }
        return await self._post(url, json.dumps(payload))

    @measure_time_async
    async def _status_run(self, thread_id: str, run_id: str):
        url = f"{self.endpoint}/threads/{thread_id}/runs/{run_id}?api-version={self.api_version}"
        return await self._get(url)

    @measure_time_async
    async def _get_response(self, thread_id: str):
        url = f"{self.endpoint}/threads/{thread_id}/messages?api-version={self.api_version}"
        return await self._get(url)
    # endregion

    # region Public methods
    async def init_agent_threads(self) -> None:
        """
        Initialize agent and thread
        """

        results = await asyncio.gather(
            self._create_agent(),
            self._create_thread()
        )

        self.agent_id = results[0]["id"]
        self.thread_id = results[1]["id"]

        print(f"Agent ID: {self.agent_id}, Thread ID: {self.thread_id}")

    async def search(self, query: str) -> any:
        """
        Perform a search using the Bing Search API

        Args:
            query: Search query

        Returns:
            Search results
        """
        await self.init_agent_threads()

        await self._ask_to_thread(self.thread_id, query)
        runs_result = await self._runs(self.thread_id, self.agent_id)
        status_run_result = await self._status_run(self.thread_id, runs_result["id"])

        while status_run_result["status"] not in ["completed", "failed"]:
            print(f"Run status: {status_run_result['status']}")

            if status_run_result["status"] == "incomplete":
                raise Exception(f"Run is incomplete. details:{status_run_result['incomplete_details']}")

            await asyncio.sleep(1)
            status_run_result = await self._status_run(self.thread_id, runs_result["id"])

        response_result = await self._get_response(self.thread_id)
        return response_result["data"]

    async def delete_agent_threads(self):
        """
        Delete agent and thread
        """
        if self.agent_id:
            await self._delete_agent(self.agent_id)
            print(f"Agent {self.agent_id} deleted.")

        if self.thread_id:
            await self._delete_thread(self.thread_id)
            print(f"Thread {self.thread_id} deleted.")
    # endregion

    # region test purpose methods
    async def _delete_all_threads(self):
        """
        Deletes all threads from the service.

        Warning:
            This method deletes all threads and should be used with caution.
        """
        url = f"{self.endpoint}/threads?api-version={self.api_version}"
        results = await self._get(url)
        while results["has_more"]:
            for thread in results["data"]:
                thread_id = thread["id"]
                print(f"Deleting thread {thread_id}...")
                await self._delete_thread(thread_id)
                print(f"Thread {thread_id} deleted.")
            if not results["has_more"]:
                break
            results = await self._get(url)

    async def _delete_all_agents(self):
        """
        Deletes all agents from the service.

        Warning:
            This method deletes all agents and should be used with caution.
        """
        url = f"{self.endpoint}/assistants?api-version={self.api_version}"
        results = await self._get(url)
        while results["has_more"]:
            for agent in results["data"]:
                agent_id = agent["id"]
                print(f"Deleting agent {agent_id}...")
                await self._delete_agent(agent_id)
                print(f"Agent {agent_id} deleted.")
            if not results["has_more"]:
                break
            results = await self._get(url)

    # endregion

class SearchConfiguration(BaseModel):
    """
    Bing Search API search configuration model
    """
    connection_id: str = Field(None, description="Bing Search connection ID")
    count: int = Field(7, description="Number of search results")
    market: str = Field("en-US", description="Market code")
    set_lang: str = Field("en", description="Language setting")
    freshness: str = Field((datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), description="Freshness setting")

class BingGrounding(BaseModel):
    """
    Bing Search API grounding configuration model
    """
    search_configurations: list[SearchConfiguration] = Field(default_factory=lambda: [SearchConfiguration()], description="List of search configurations")

class Tool(BaseModel):
    """
    Bing Search API tool model
    """
    type: str = Field("bing_grounding", description="Tool type")
    bing_grounding: BingGrounding = Field(default=BingGrounding(), description="Bing Search grounding configuration")

class CreateAgentRequest(BaseModel):
    """
    Bing Search API agent creation request model
    """
    instructions: str = Field("You are a helpful agent.", description="Agent instructions")
    name: str = Field("my-agent", description="Agent name")
    model: str = Field("gpt-4o", description="Model to use")
    tools: list[Tool] = Field(default_factory=lambda: [Tool()], description="List of tools to use")

    def serialize(self) -> str:
        """
        Serialize the model to a JSON string

        Returns:
            JSON string
        """
        return self.model_dump_json(exclude_none=True, indent=None)

