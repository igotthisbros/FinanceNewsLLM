import os
import json
import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    SystemMessage, UserMessage, AssistantMessage, ToolMessage,
    ChatCompletionsToolDefinition, FunctionDefinition
)
from azure.core.credentials import AzureKeyCredential

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

client = ChatCompletionsClient(
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(GITHUB_TOKEN)
)


async def main():
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["mock_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # Get tools from MCP server
            tools_response = await session.list_tools()
            print(f"Connected to MCP server!")
            print(f"Available tools:")
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Convert MCP tools to Azure format
            azure_tools = []
            for tool in tools_response.tools:
                azure_tools.append(
                    ChatCompletionsToolDefinition(
                        function=FunctionDefinition(
                            name=tool.name,
                            description=tool.description,
                            parameters=tool.inputSchema
                        )
                    )
                )
            
            # Chat loop
            messages = [
                SystemMessage(content="You are a helpful assistant with access to tools.")
            ]
            
            print("\nChat ready! Type 'quit' to exit.\n")
            
            while True:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                messages.append(UserMessage(content=user_input))
                
                # Call LLM with tools
                response = client.complete(
                    model="Llama-3.3-70B-Instruct",
                    messages=messages,
                    tools=azure_tools
                )
                
                assistant_message = response.choices[0].message
                
                # Check if LLM wants to use a tool
                if assistant_message.tool_calls:
                    tool_call = assistant_message.tool_calls[0]
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[Calling MCP tool: {tool_name}({tool_args})]")
                    
                    # Execute tool on MCP server
                    result = await session.call_tool(tool_name, tool_args)
                    result_text = result.content[0].text if result.content else "No result"
                    
                    print(f"[Tool returned: {result_text}]")
                    
                    # Add to conversation
                    messages.append(AssistantMessage(content="", tool_calls=[tool_call]))
                    messages.append(ToolMessage(content=result_text, tool_call_id=tool_call.id))
                    
                    # Get final response
                    response = client.complete(
                        model="Llama-3.3-70B-Instruct",
                        messages=messages,
                        tools=azure_tools
                    )
                    
                    assistant_message = response.choices[0].message
                
                # Print response
                messages.append(AssistantMessage(content=assistant_message.content))
                print(f"\nAssistant: {assistant_message.content}\n")


if __name__ == "__main__":
    asyncio.run(main())