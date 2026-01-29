# Atlassian MCP Setup Guide (Updated)

Your agent now has the `mcp_client` tool for connecting to Atlassian's MCP server and accessing Jira and Confluence!

## How It Works

The agent uses the `mcp_client` tool to dynamically connect to MCP servers. For Atlassian, it connects to `https://mcp.atlassian.com/v1/sse` using streamable HTTP transport.

## First-Time Setup

**Step 1: Connect to Atlassian MCP Server**

Run your agent:
```bash
python cc_agent_main.py
```

**Step 2: Ask the agent to connect**
```
Enter a command: Connect to Atlassian MCP server at https://mcp.atlassian.com/v1/sse using streamable_http transport with connection ID 'atlassian'
```

The agent will use the `mcp_client` tool to establish the connection.

**Step 3: Complete OAuth (if prompted)**
- You may be prompted to authorize via OAuth
- Follow the authorization URL
- Log in to your Atlassian account
- Click "Allow"

**Step 4: Load Atlassian tools**
```
Enter a command: Load tools from the atlassian MCP connection
```

This makes Jira and Confluence tools available to the agent.

## Simplified Usage

Once connected, you can ask the agent to handle the connection automatically:

```
Enter a command: Search Jira for bugs assigned to me
```

The agent will:
1. Check if connected to Atlassian MCP
2. Connect if needed
3. Use the appropriate Jira tool
4. Return results

## Example Commands

### Initial Connection
```
Connect to Atlassian MCP server for Jira and Confluence access
```

### Jira Commands
- "Search Jira for bugs assigned to me"
- "Create a Jira issue titled 'Fix login bug' in project ABC"
- "List all open issues in project XYZ"
- "Get details of issue ABC-123"

### Confluence Commands
- "Search Confluence for 'API documentation'"
- "Get content from Confluence page titled 'Getting Started'"
- "List recent Confluence pages"

## Manual MCP Client Usage

You can also use the `mcp_client` tool directly:

**Connect:**
```python
# Agent will execute:
mcp_client(
    action="connect",
    connection_id="atlassian",
    transport="streamable_http",
    server_url="https://mcp.atlassian.com/v1/sse"
)
```

**List available tools:**
```python
mcp_client(
    action="list_tools",
    connection_id="atlassian"
)
```

**Call a tool:**
```python
mcp_client(
    action="call_tool",
    connection_id="atlassian",
    tool_name="jira_search_issues",
    tool_args={"jql": "assignee = currentUser() AND status = Open"}
)
```

## Benefits

✅ **Dynamic Connection:** Connect to any MCP server on demand
✅ **Works Everywhere:** Local development AND AWS Bedrock AgentCore
✅ **Multiple Servers:** Connect to multiple MCP servers simultaneously
✅ **Flexible:** Use different transport types (stdio, streamable_http)

## Troubleshooting

**Issue: "Failed to connect to MCP server"**
- Check internet connection
- Verify the server URL is correct
- Ensure you have Atlassian Cloud access

**Issue: "Tool not found"**
- Make sure you've loaded tools: "Load tools from atlassian connection"
- List available tools: "List tools from atlassian MCP server"

**Issue: "Connection not found"**
- Connect first: "Connect to Atlassian MCP server"
- Check active connections: "List all MCP connections"

## Deployment to AWS

When deploying to AWS Bedrock AgentCore:
- ✅ **No code changes needed!**
- ✅ `mcp_client` tool works the same way
- ✅ Streamable HTTP transport is cloud-compatible
- ✅ OAuth tokens persist across sessions
