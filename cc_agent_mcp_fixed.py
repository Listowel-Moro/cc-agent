from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import http_request, generate_image
from strands_tools.tavily import tavily_search
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient
from datetime import datetime
import os
from dotenv import load_dotenv


# load environment variables
load_dotenv()

# Define custom tools using the @tool decorator

@tool
def get_current_datetime() -> str:
    """
    Get the current date and time.
    
    Returns:
        Current date and time in a readable format
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """
    Perform mathematical calculations safely.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")
    
    Returns:
        The result of the calculation
    """
    try:
        # Only allow safe mathematical operations
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression. Only numbers and basic operators (+, -, *, /) are allowed."
        
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        filename: Name of the file to write
        content: Content to write to the file
    
    Returns:
        Success or error message
    """
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def read_file(filename: str) -> str:
    """
    Read content from a file.
    
    Args:
        filename: Name of the file to read
    
    Returns:
        File content or error message
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """
    List files in a directory.
    
    Args:
        directory: Directory path to list (defaults to current directory)
    
    Returns:
        List of files and directories
    """
    try:
        items = os.listdir(directory)
        files = [f for f in items if os.path.isfile(os.path.join(directory, f))]
        dirs = [d for d in items if os.path.isdir(os.path.join(directory, d))]
        
        result = f"Directory: {directory}\n\n"
        result += f"Directories ({len(dirs)}):\n"
        for d in dirs:
            result += f"  [DIR] {d}\n"
        result += f"\nFiles ({len(files)}):\n"
        for f in files:
            result += f"  [FILE] {f}\n"
        
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# Configure the agent with tools
model = BedrockModel(model_id="us.amazon.nova-lite-v1:0")

print("\nStrands Agent with MCP Atlassian Integration (Windows)")
print("=" * 60)

# Create MCP client for Atlassian using proper Windows stdio format
print("\n[INFO] Initializing Atlassian MCP client...")
try:
    # Windows-specific stdio parameters following Strands documentation
    mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            # args=[
            #     "--from",
            #     "mcp-atlassian",  # Package name from PyPI
            #     "mcp-atlassian"    # Executable name (without .exe, uvx handles it)
            # ],
            args=[
            "--from",
            "awslabs.aws-documentation-mcp-server@latest",
            "awslabs.aws-documentation-mcp-server.exe"
        ]
            # env={
            #     "JIRA_URL": os.getenv("JIRA_URL"),
            #     "JIRA_USERNAME": os.getenv("JIRA_USERNAME"),
            #     "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
            #     "CONFLUENCE_URL": os.getenv("CONFLUENCE_URL"),
            #     "CONFLUENCE_USERNAME": os.getenv("CONFLUENCE_USERNAME"),
            #     "CONFLUENCE_API_TOKEN": os.getenv("CONFLUENCE_API_TOKEN"),
            # }
        )
    ))
    
    # Use context manager as per Strands documentation
    with mcp_client:
        print("[INFO] Loading tools from MCP server...")
        mcp_tools = mcp_client.list_tools_sync()
        print(f"[OK] Loaded {len(mcp_tools)} tools from Atlassian MCP server!")
        
        # Create agent with MCP tools
        agent = Agent(
            model=model,
            tools=mcp_tools
            # tools=[
            #     get_current_datetime,
            #     calculate,
            #     write_file,
            #     read_file,
            #     list_files,
            #     http_request,
            #     generate_image,
            #     tavily_search,
            #     *mcp_tools  # Add all Atlassian MCP tools
            # ]
        )

        response = agent("What is AWS Lambda?")
        print(response.message)
        
        # print("\n" + "=" * 60)
        # print("\n[Available Tools]")
        # print("\n[Standard Tools]:")
        # print("  - get_current_datetime, calculate")
        # print("  - write_file, read_file, list_files")
        # print("  - http_request, generate_image, tavily_search")
        # print(f"\n[Atlassian MCP Tools]: {len(mcp_tools)} tools loaded")
        # print("  (Jira and Confluence operations)")
        # print("\n" + "=" * 60)
        
        # # Verify credentials
        # if not all([os.getenv("JIRA_URL"), os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")]):
        #     print("\n[WARNING] Jira credentials not fully configured in .env file")
        # if not all([os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]):
        #     print("[WARNING] Confluence credentials not fully configured in .env file")
        
        # if all([os.getenv("JIRA_URL"), os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN"), 
        #         os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]):
        #     print("\n[OK] All Atlassian credentials configured!")
        #     print(f"   Jira URL: {os.getenv('JIRA_URL')}")
        #     print(f"   Confluence URL: {os.getenv('CONFLUENCE_URL')}")
        
        # print("\n" + "=" * 60)
        
        # Interactive loop
        # while True:
        #     test_command = input("\nEnter a command (or 'exit' to quit): ")
            
        #     if test_command.lower() in ['exit', 'quit', 'q']:
        #         print("\nGoodbye!")
        #         break
            
        #     if not test_command.strip():
        #         continue
            
        #     print("\n" + "=" * 60)
        #     print("Agent Response:")
        #     print("=" * 60 + "\n")
            
        #     try:
        #         response = agent(test_command)
        #         print(response)
        #     except Exception as e:
        #         print(f"[ERROR] {e}")
            
        #     print("\n" + "=" * 60)

except Exception as e:
    print(f"\n[ERROR] Failed to initialize Atlassian MCP client: {e}")
    print("\nPossible solutions:")
    print("  1. Make sure 'uv' is installed: pip install uv")
    print("  2. Make sure 'uvx' is accessible from command line")
    print("  3. Check your .env file has all Atlassian credentials")
    print("  4. Try running: uvx --from mcp-atlassian mcp-atlassian --help")
    print("\nFalling back to agent without MCP tools...")
    
    # Fallback: create agent without MCP tools
    agent = Agent(
        model=model,
        tools=[
            get_current_datetime,
            calculate,
            write_file,
            read_file,
            list_files,
            http_request,
            generate_image,
            tavily_search
        ]
    )
    
    print("\n" + "=" * 60)
    print("\nAgent running WITHOUT Atlassian MCP integration")
