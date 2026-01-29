from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import http_request, generate_image
from strands_tools.tavily import tavily_search
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
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

# Create MCP client for Atlassian (self-hosted via stdio)
print("Initializing Atlassian MCP client...")
try:
    # Create server parameters
    # Use python to run mcp-atlassian directly (more reliable on Windows)
    import sys
    
    server_params = StdioServerParameters(
        command=sys.executable,  # Use current Python interpreter
        args=["-m", "mcp_atlassian"],
        env={
            "JIRA_URL": os.getenv("JIRA_URL"),
            "JIRA_USERNAME": os.getenv("JIRA_USERNAME"),
            "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
            "CONFLUENCE_URL": os.getenv("CONFLUENCE_URL"),
            "CONFLUENCE_USERNAME": os.getenv("CONFLUENCE_USERNAME"),
            "CONFLUENCE_API_TOKEN": os.getenv("CONFLUENCE_API_TOKEN"),
        }
    )
    
    # MCPClient expects a callable that returns the transport
    atlassian_mcp = MCPClient(
        lambda: stdio_client(server_params)
    )
    print("[OK] Atlassian MCP client initialized successfully!")
    mcp_tools = [atlassian_mcp]
except Exception as e:
    print(f"[WARNING] Could not initialize Atlassian MCP: {e}")
    print("  Make sure you've configured your .env file with Atlassian credentials")
    mcp_tools = []

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
        tavily_search,
        *mcp_tools  # Add Atlassian MCP if available
    ]
)

print("\nStrands Agent with Tools")
print("=" * 50)
print("\nAvailable Tools:")
print("  - get_current_datetime: Get current date and time")
print("  - calculate: Perform math calculations")
print("  - write_file: Write content to a file")
print("  - read_file: Read content from a file")
print("  - list_files: List files in a directory")
print("  - http_request: Make HTTP requests to APIs")
print("  - generate_image: Generate AI images using AWS Bedrock")
print("  - tavily_search: Search the web for real-time information")
if mcp_tools:
    print("  - Atlassian MCP: Access Jira and Confluence (via self-hosted MCP server)")
print("=" * 50)

test_command = input("\nEnter a command: ")

print("\n" + "=" * 50)
print("Agent Response:")
print("=" * 50 + "\n")

try:
    response = agent(test_command)
    print(response)
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
