from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import http_request, generate_image, mcp_client
from strands_tools.tavily import tavily_search
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
        mcp_client  # Dynamic MCP client for Atlassian and other MCP servers
    ]
)

print("Strands Agent with Tools")
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
print("  - mcp_client: Connect to MCP servers (Atlassian, etc.) for Jira/Confluence access")
print("=" * 50)

# Auto-connect to Atlassian MCP server on startup
print("\n[INFO] Connecting to Atlassian MCP server...")
try:
    connect_result = agent(
        "Use the mcp_client tool to connect to the Atlassian MCP server at https://mcp.atlassian.com/v1/sse "
        "using streamable_http transport with connection ID 'atlassian'. Then load all tools from this connection."
    )
    print("[SUCCESS] Atlassian MCP connected! Jira and Confluence tools are now available.")
except Exception as e:
    print(f"[WARNING] Could not auto-connect to Atlassian: {e}")
    print("[INFO] You can manually connect by asking: 'Connect to Atlassian MCP server'")

print("=" * 50)

# Main interaction loop
while True:
    test_command = input("\nEnter a command (or 'exit' to quit): ")
    
    if test_command.lower() in ['exit', 'quit', 'q']:
        print("\nGoodbye!")
        break
    
    print("\n" + "=" * 50)
    print("Agent Response:")
    print("=" * 50 + "\n")
    
    try:
        response = agent(test_command)
        print(response)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
