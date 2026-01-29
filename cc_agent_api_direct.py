from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import http_request, generate_image
from strands_tools.tavily import tavily_search
from datetime import datetime
import os
import json
import base64
import requests  # Use standard requests library for HTTP calls
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Atlassian configuration
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")


def get_jira_auth_headers():
    """Get authentication headers for Jira API calls."""
    auth_str = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    return {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json"
    }


def get_confluence_auth_headers():
    """Get authentication headers for Confluence API calls."""
    auth_str = f"{CONFLUENCE_USERNAME}:{CONFLUENCE_API_TOKEN}"
    auth_bytes = auth_str.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    return {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json"
    }


# ============= JIRA TOOLS =============

@tool
def jira_search_issues(jql: str, max_results: int = 50) -> str:
    """
    Search for Jira issues using JQL (Jira Query Language).
    
    Args:
        jql: JQL query string (e.g., "project = PROJ AND status = Open")
        max_results: Maximum number of results to return (default: 50)
    
    Returns:
        JSON string containing search results with issue keys, summaries, and statuses
    """
    try:
        # Use the new /search/jql endpoint (migrated from /search in August 2025)
        url = f"{JIRA_URL}/rest/api/3/search/jql"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,priority,created,updated"
        }
        
        response = requests.get(url, headers=get_jira_auth_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        
        if "issues" in data:
            issues = []
            for issue in data["issues"]:
                issues.append({
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "status": issue["fields"]["status"]["name"],
                    "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"].get("assignee") else "Unassigned",
                    "priority": issue["fields"]["priority"]["name"] if issue["fields"].get("priority") else "None",
                    "created": issue["fields"]["created"],
                    "updated": issue["fields"]["updated"]
                })
            return json.dumps({"total": data["total"], "issues": issues}, indent=2)
        return json.dumps(data, indent=2)
    except requests.exceptions.HTTPError as e:
        return f"Error searching Jira (HTTP {e.response.status_code}): {e.response.text}"
    except Exception as e:
        return f"Error searching Jira: {str(e)}"


@tool
def jira_get_issue(issue_key: str) -> str:
    """
    Get detailed information about a specific Jira issue.
    
    Args:
        issue_key: The issue key (e.g., "PROJ-123")
    
    Returns:
        JSON string with detailed issue information
    """
    try:
        url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
        
        response = requests.get(url, headers=get_jira_auth_headers())
        response.raise_for_status()
        data = response.json()
        issue_info = {
            "key": data["key"],
            "summary": data["fields"]["summary"],
            "description": data["fields"].get("description", "No description"),
            "status": data["fields"]["status"]["name"],
            "assignee": data["fields"]["assignee"]["displayName"] if data["fields"].get("assignee") else "Unassigned",
            "reporter": data["fields"]["reporter"]["displayName"] if data["fields"].get("reporter") else "Unknown",
            "priority": data["fields"]["priority"]["name"] if data["fields"].get("priority") else "None",
            "created": data["fields"]["created"],
            "updated": data["fields"]["updated"],
            "issue_type": data["fields"]["issuetype"]["name"]
        }
        return json.dumps(issue_info, indent=2)
    except Exception as e:
        return f"Error getting Jira issue: {str(e)}"


@tool
def jira_create_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> str:
    """
    Create a new Jira issue.
    
    Args:
        project_key: The project key (e.g., "PROJ")
        summary: Issue summary/title
        description: Issue description
        issue_type: Type of issue (default: "Task", can be "Bug", "Story", etc.)
    
    Returns:
        JSON string with created issue information
    """
    try:
        url = f"{JIRA_URL}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": issue_type}
            }
        }
        
        response = requests.post(url, headers=get_jira_auth_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        return json.dumps({
            "success": True,
            "key": data.get("key"),
            "id": data.get("id"),
            "url": f"{JIRA_URL}/browse/{data.get('key')}"
        }, indent=2)
    except Exception as e:
        return f"Error creating Jira issue: {str(e)}"


@tool
def jira_update_issue(issue_key: str, summary: str = None, description: str = None, status: str = None) -> str:
    """
    Update a Jira issue.
    
    Args:
        issue_key: The issue key (e.g., "PROJ-123")
        summary: New summary (optional)
        description: New description (optional)
        status: New status (optional, e.g., "In Progress", "Done")
    
    Returns:
        Success or error message
    """
    try:
        url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
        
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }
        
        if fields:
            payload = {"fields": fields}
            response = requests.put(url, headers=get_jira_auth_headers(), json=payload)
            response.raise_for_status()
        
        # Handle status transition separately
        if status:
            transitions_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
            transitions_response = requests.get(transitions_url, headers=get_jira_auth_headers())
            transitions_response.raise_for_status()
            transitions_data = transitions_response.json()
            
            # Find the transition ID for the requested status
            transition_id = None
            for transition in transitions_data.get("transitions", []):
                if transition["to"]["name"].lower() == status.lower():
                    transition_id = transition["id"]
                    break
            
            if transition_id:
                transition_payload = {
                    "transition": {"id": transition_id}
                }
                response = requests.post(transitions_url, headers=get_jira_auth_headers(), json=transition_payload)
                response.raise_for_status()
            else:
                return f"Warning: Could not find transition to status '{status}'. Fields updated successfully."
        
        return json.dumps({"success": True, "message": f"Issue {issue_key} updated successfully"})
    except Exception as e:
        return f"Error updating Jira issue: {str(e)}"


@tool
def jira_add_comment(issue_key: str, comment: str) -> str:
    """
    Add a comment to a Jira issue.
    
    Args:
        issue_key: The issue key (e.g., "PROJ-123")
        comment: The comment text
    
    Returns:
        Success or error message
    """
    try:
        url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/comment"
        
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(url, headers=get_jira_auth_headers(), json=payload)
        response.raise_for_status()
        
        return json.dumps({"success": True, "message": f"Comment added to {issue_key}"})
    except Exception as e:
        return f"Error adding comment: {str(e)}"


# ============= CONFLUENCE TOOLS =============

@tool
def confluence_search_content(query: str, limit: int = 25) -> str:
    """
    Search for Confluence content.
    
    Args:
        query: Search query string
        limit: Maximum number of results (default: 25)
    
    Returns:
        JSON string with search results
    """
    try:
        url = f"{CONFLUENCE_URL}/wiki/rest/api/content/search"
        params = {
            "cql": f"text ~ \"{query}\"",
            "limit": limit
        }
        
        response = requests.get(url, headers=get_confluence_auth_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        if "results" in data:
            results = []
            for item in data["results"]:
                results.append({
                    "id": item["id"],
                    "title": item["title"],
                    "type": item["type"],
                    "url": f"{CONFLUENCE_URL}/wiki{item['_links']['webui']}"
                })
            return json.dumps({"total": data.get("totalSize", len(results)), "results": results}, indent=2)
        return response
    except Exception as e:
        return f"Error searching Confluence: {str(e)}"


@tool
def confluence_get_page(page_id: str) -> str:
    """
    Get content from a Confluence page.
    
    Args:
        page_id: The page ID
    
    Returns:
        JSON string with page content
    """
    try:
        url = f"{CONFLUENCE_URL}/wiki/rest/api/content/{page_id}"
        params = {
            "expand": "body.storage,version"
        }
        
        response = http_request(
            url=url,
            method="GET",
            headers=get_confluence_auth_headers(),
            params=params
        )
        
        data = json.loads(response)
        page_info = {
            "id": data["id"],
            "title": data["title"],
            "type": data["type"],
            "version": data["version"]["number"],
            "content": data["body"]["storage"]["value"],
            "url": f"{CONFLUENCE_URL}/wiki{data['_links']['webui']}"
        }
        return json.dumps(page_info, indent=2)
    except Exception as e:
        return f"Error getting Confluence page: {str(e)}"


@tool
def confluence_list_spaces() -> str:
    """
    List all Confluence spaces.
    
    Returns:
        JSON string with list of spaces
    """
    try:
        url = f"{CONFLUENCE_URL}/wiki/rest/api/space"
        params = {
            "limit": 50
        }
        
        response = http_request(
            url=url,
            method="GET",
            headers=get_confluence_auth_headers(),
            params=params
        )
        
        data = json.loads(response)
        if "results" in data:
            spaces = []
            for space in data["results"]:
                spaces.append({
                    "key": space["key"],
                    "name": space["name"],
                    "type": space["type"]
                })
            return json.dumps({"spaces": spaces}, indent=2)
        return response
    except Exception as e:
        return f"Error listing Confluence spaces: {str(e)}"


# ============= BASIC UTILITY TOOLS =============

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


# ============= CONFIGURE AND RUN AGENT =============

# Initialize the model
model = BedrockModel(model_id="us.amazon.nova-lite-v1:0")

# Create the agent with all tools
agent = Agent(
    model=model,
    tools=[
        # Jira tools
        jira_search_issues,
        jira_get_issue,
        jira_create_issue,
        jira_update_issue,
        jira_add_comment,
        # Confluence tools
        confluence_search_content,
        confluence_get_page,
        confluence_list_spaces,
        # Utility tools
        get_current_datetime,
        calculate,
        write_file,
        read_file,
        list_files,
        # External tools
        http_request,
        generate_image,
        tavily_search
    ]
)

print("\nStrands Agent with Direct Atlassian API Integration")
print("=" * 60)
print("\n[Available Tools]")
print("\n[Jira Tools]:")
print("  - jira_search_issues: Search for issues using JQL")
print("  - jira_get_issue: Get detailed info about a specific issue")
print("  - jira_create_issue: Create a new issue")
print("  - jira_update_issue: Update an existing issue")
print("  - jira_add_comment: Add a comment to an issue")
print("\n[Confluence Tools]:")
print("  - confluence_search_content: Search for Confluence content")
print("  - confluence_get_page: Get content from a specific page")
print("  - confluence_list_spaces: List all Confluence spaces")
print("\n[Utility Tools]:")
print("  - get_current_datetime: Get current date and time")
print("  - calculate: Perform math calculations")
print("  - write_file, read_file, list_files: File operations")
print("  - http_request: Make HTTP requests to APIs")
print("  - generate_image: Generate AI images")
print("  - tavily_search: Search the web")
print("\n" + "=" * 60)

# Verify credentials are configured
if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
    print("\n[WARNING] Jira credentials not fully configured in .env file")
if not all([CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN]):
    print("[WARNING] Confluence credentials not fully configured in .env file")

if all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN]):
    print("\n[OK] All Atlassian credentials configured!")
    print(f"   Jira URL: {JIRA_URL}")
    print(f"   Confluence URL: {CONFLUENCE_URL}")

print("\n" + "=" * 60)

# Interactive loop
while True:
    command = input("\nEnter a command (or 'exit' to quit): ")
    
    if command.lower() in ['exit', 'quit', 'q']:
        print("\nGoodbye!")
        break
    
    if not command.strip():
        continue
    
    print("\n" + "=" * 60)
    print("Agent Response:")
    print("=" * 60 + "\n")
    
    try:
        response = agent(command)
        print(response)
    except Exception as e:
        print(f"[ERROR] {e}")
    
    print("\n" + "=" * 60)
