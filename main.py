import asyncio
import datetime
import os
from datetime import datetime, timedelta

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import \
    FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import \
    AzureChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory, StreamingChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import KernelArguments
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from grounding.bing.bing_search import GroundingWithBingSearch

# Environment variables are loaded from the .env file
load_dotenv()

class BingSearchPlugin:
    def __init__(self):
        azure_ai_foundry_project_endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
        api_version = os.getenv("AZURE_AI_FOUNDRY_API_VERSION", "2025-05-15-preview")
        bing_search_connection_id = os.getenv("BING_SEARCH_CONNECTION_ID")
        self.search_client = GroundingWithBingSearch(endpoint=azure_ai_foundry_project_endpoint, credential=DefaultAzureCredential(),api_version=api_version, connection_id=bing_search_connection_id)

    @kernel_function(
        description="Performs a web search using Bing, returning relevant results for grounding LLM responses.",
        name="bing_search"
    )
    async def bing_search(self, query: str):
        print("----------------------------------------------------------")
        print("Start Grounding with Bing Search")
        result = await self.search_client.search(query)
        print("----------------------------------------------------------")
        print(f"Search result: {result}")
        print("----------------------------------------------------------")
        yield result
        await self.search_client.delete_agent_threads()

async def main():
    """Main function - Example execution"""
    try:
        kernel = Kernel()
        kernel.add_plugin(BingSearchPlugin(), plugin_name="BingSearch")

        # Define a chat function (a template for how to handle user input).
        chat_function = kernel.add_function(
            prompt="{{$chat_history}}{{$user_input}}",
            plugin_name="ChatBot",
            function_name="chat",
        )

        chat_completion = AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            base_url=os.getenv("AZURE_OPENAI_BASE_URL")
        )

        kernel.add_service(chat_completion)

        execution_settings = AzureChatPromptExecutionSettings()
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Pass the request settings to the kernel arguments.
        arguments = KernelArguments(settings=execution_settings)

        chat_history = ChatHistory()

        print("----------------------------------------------------------")
        print("Assistant > ", end="", flush=True)

        # Initiate a back-and-forth chat
        user_input = None
        while True:
            # Collect user input
            user_input = f"tell me yesterday's {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')} Tesla news" if user_input is None else input("User > ")

            # Terminate the loop if the user says "exit"
            if user_input == "exit":
                break

            # Add user input to the history
            chat_history.add_user_message(user_input)

            arguments["user_input"] = user_input
            arguments["chat_history"] = chat_history

            streamed_response_chunks: list[StreamingChatMessageContent] = []

            async for message in kernel.invoke_stream(
                chat_function,
                return_function_results=False,
                arguments=arguments,
            ):
                msg = message[0]

                # We only expect assistant messages here.
                if not isinstance(msg, StreamingChatMessageContent) or msg.role != AuthorRole.ASSISTANT:
                    continue

                streamed_response_chunks.append(msg)
                print(str(msg), end="", flush=True)

            print("\n", flush=True)

            if streamed_response_chunks:
                result = "".join([str(content) for content in streamed_response_chunks])
                chat_history.add_user_message(user_input)
                chat_history.add_assistant_message(result)

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    print("Semantic Kernel with Bing Search Grounding started...")
    asyncio.run(main())
