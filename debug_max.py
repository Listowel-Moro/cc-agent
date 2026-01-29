from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models.bedrock import BedrockModel
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()


model = BedrockModel(model_id="us.amazon.nova-lite-v1:0")

# For Windows:
stdio_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        # args=[
        #     "--from",
        #     "awslabs.aws-documentation-mcp-server@latest",
        #     "awslabs.aws-documentation-mcp-server.exe"
        # ]
        args=[
                "--from",
                "mcp-atlassian",  # Package name from PyPI
                "mcp-atlassian"    # Executable name (without .exe, uvx handles it)
            ],
            env={
                "JIRA_URL": os.getenv("JIRA_URL"),
                "JIRA_USERNAME": os.getenv("JIRA_USERNAME"),
                "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
                "CONFLUENCE_URL": os.getenv("CONFLUENCE_URL"),
                "CONFLUENCE_USERNAME": os.getenv("CONFLUENCE_USERNAME"),
                "CONFLUENCE_API_TOKEN": os.getenv("CONFLUENCE_API_TOKEN"),
            }
    )
))

with stdio_mcp_client:
    tools = stdio_mcp_client.list_tools_sync()
    agent = Agent(model=model,tools=tools)
    response = agent("check my jira projects and let me know what open issues I have")
    print(response.message)