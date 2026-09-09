import os
import json
from dotenv import load_dotenv
from unittest import result

from openai import AsyncAzureOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)

llm = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

async def main():

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to MCP server")

            tools = await session.list_tools()
            for tool in tools.tools:
                print("Name:", tool.name)
                print("Description:", tool.description)
                print("Input Schema:", tool.input_schema)
                print()

            openai_tools = []
            for tool in tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema,
                    }
                })

            question = input("What would you like to know? ")

            response = await llm.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                tools=openai_tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_arguments = json.loads(tool_call.function.arguments)

            print("Selected tool:", tool_name)
            print("Arguments:", tool_arguments)

            result = await session.call_tool(
                                            tool_name,
                                            tool_arguments
                                            )

            # print(result.content[0].text)

            messages = [
                        {
                            "role": "user",
                            "content": question
                        },
                        {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": tool_name,
                                        "arguments": tool_call.function.arguments
                                    }
                                }
                            ]
                        },
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result.content[0].text
                        }
                    ]
            
            final_response = await llm.chat.completions.create(
                                model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
                                messages=messages
                            )

            print("\nFinal Answer:")
            print(final_response.choices[0].message.content)

            prompts = await session.list_prompts()
            for prompt in prompts.prompts:
                print("Prompt:", prompt.name)
                print("Description:", prompt.description)

            company = input("Enter company name for competitive analysis: ")

            prompt_result = await session.get_prompt(
                "competitor_analysis_prompt",
                arguments={"company": company}
            )

            print("\nGenerated Prompt:")
            print(prompt_result.messages[0].content.text)

            prompt_text = prompt_result.messages[0].content.text
            response = await llm.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
                messages=[
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ]
            )

            print("\nLLM Response:")
            print(response.choices[0].message.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

            