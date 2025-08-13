#!/usr/bin/env python3
"""
Test script for the Semantic Kernel with Bing Search project
"""

import os
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from grounding.bing.bing_search import GroundingWithBingSearch

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


async def test_bing_search():
    """Bing Search feature test"""
    print("\n🔍 Running Bing Search test...")

    try:
        load_dotenv()

        azure_ai_foundry_project_endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
        bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")
        api_version = os.getenv("AZURE_AI_FOUNDRY_API_VERSION", "2025-05-15-preview")
        bing_search_connection_id = os.getenv("BING_SEARCH_CONNECTION_ID")

        search_client = GroundingWithBingSearch(endpoint=azure_ai_foundry_project_endpoint, credential=DefaultAzureCredential(), api_version=api_version, connection_id=bing_search_connection_id)
        result = await search_client.search("let me know the news about OpenAI")

        print("Search results:", result)


    except Exception as e:
        print(e)

async def test_delete_threads():
    """Bing Search thread deletion test"""
    print("\n🗑️ Running Bing Search thread deletion test...")
    load_dotenv()

    azure_ai_foundry_project_endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
    bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-05-15-preview")
    bing_search_connection_id = os.getenv("BING_SEARCH_CONNECTION_ID")

    search_client = GroundingWithBingSearch(endpoint=azure_ai_foundry_project_endpoint, credential=DefaultAzureCredential(), api_version=api_version, connection_id=bing_search_connection_id)

    await search_client._delete_all_threads()

async def test_delete_agents():
    """Bing Search agent deletion test"""
    print("\n🗑️ Running Bing Search agent deletion test...")
    load_dotenv()

    azure_ai_foundry_project_endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
    bing_search_api_key = os.getenv("BING_SEARCH_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-05-15-preview")
    bing_search_connection_id = os.getenv("BING_SEARCH_CONNECTION_ID")

    search_client = GroundingWithBingSearch(endpoint=azure_ai_foundry_project_endpoint, credential=DefaultAzureCredential(), api_version=api_version, connection_id=bing_search_connection_id)

    await search_client._delete_all_agents()


