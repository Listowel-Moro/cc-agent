# Self-Hosted Atlassian MCP Setup

Your agent is now configured to use a self-hosted Atlassian MCP server via stdio transport!

## Setup Steps

### 1. Configure Your .env File

Open `.env` and replace the placeholders with your actual Atlassian credentials:

```env
# Atlassian API Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-actual-api-token

CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-actual-api-token
```

**Get your API token:**
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Strands Agent")
4. Copy the token and paste it in your `.env` file

**Important:**
- Replace `your-domain` with your actual Atlassian domain
- Use the same API token for both Jira and Confluence (they share tokens)
- Use your Atlassian account email for both usernames

### 2. Run Your Agent

```bash
python cc_agent_main.py
```

You should see:
```
Initializing Atlassian MCP client...
✓ Atlassian MCP client initialized successfully!
```

### 3. Test Jira Access

```
Enter a command: List all my Jira projects
Enter a command: Search Jira for bugs assigned to me
Enter a command: Get details of issue ABC-123
```

### 4. Test Confluence Access

```
Enter a command: Search Confluence for API documentation
Enter a command: List recent Confluence pages
```

## How It Works

**Self-Hosted MCP Server:**
- Uses `npx` to run `@modelcontextprotocol/server-atlassian`
- Communicates via stdio (standard input/output)
- Runs as a subprocess when your agent starts
- Stops automatically when your agent stops

**Authentication:**
- Uses API tokens (no OAuth needed)
- Credentials loaded from `.env` file
- Passed to MCP server via environment variables

## Troubleshooting

**Error: "Could not initialize Atlassian MCP"**
- Check that Node.js is installed: `node --version`
- Verify your `.env` file has correct credentials
- Make sure there are no typos in URLs or tokens

**Error: "401 Unauthorized"**
- Your API token might be invalid
- Regenerate token at https://id.atlassian.com/manage-profile/security/api-tokens
- Make sure you're using the correct Atlassian account

**Error: "npx command not found"**
- Node.js/npm is not installed or not in PATH
- Install from: https://nodejs.org/
- Restart your terminal after installation

## Example .env File

```env
# Tavily API
TAVILY_API_KEY=tvly-dev-abc123...

# Atlassian API
JIRA_URL=https://mycompany.atlassian.net
JIRA_USERNAME=john.doe@mycompany.com
JIRA_API_TOKEN=ATATT3xFfGF0...

CONFLUENCE_URL=https://mycompany.atlassian.net
CONFLUENCE_USERNAME=john.doe@mycompany.com
CONFLUENCE_API_TOKEN=ATATT3xFfGF0...
```

## Benefits of Self-Hosted Approach

✅ **Simple Authentication:** Just API tokens, no OAuth
✅ **Works Locally:** Perfect for development
✅ **No External Dependencies:** MCP server runs locally
✅ **Full Control:** You manage the MCP server lifecycle

## Next Steps

Once you've configured your `.env` file:
1. Run `python cc_agent_main.py`
2. Test with simple Jira queries
3. Explore Confluence integration
4. Build your workflows!
