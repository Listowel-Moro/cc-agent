# Tavily API Setup Guide

The `tavily_search` tool requires a Tavily API key to search the web.

## Getting Your API Key

1. Visit [Tavily.com](https://tavily.com)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes **1,000 searches per month**

## Setting Up the API Key

### Option 1: Environment Variable (Recommended)

**Windows PowerShell:**
```powershell
$env:TAVILY_API_KEY="your-api-key-here"
```

**Windows Command Prompt:**
```cmd
set TAVILY_API_KEY=your-api-key-here
```

**Permanent (Windows):**
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `TAVILY_API_KEY`
6. Variable value: Your API key
7. Click OK

### Option 2: .env File

Create a `.env` file in your project directory:
```
TAVILY_API_KEY=your-api-key-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

Add to the top of `cc_agent_main.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Testing

Once configured, run:
```bash
python cc_agent_main.py
```

Try: "Check the web and tell me the latest football news"

The agent will now be able to search the web in real-time!
