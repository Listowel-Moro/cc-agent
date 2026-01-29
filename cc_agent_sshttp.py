from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient
import os
from strands.models.bedrock import BedrockModel


streamable_http_mcp_client = MCPClient(
    lambda: streamablehttp_client(
        url="https://mcp.atlassian.com/v1/mcp",
        headers={"Authorization": f"Bearer ATATT3xFfGF07Uha4v-LNDCLdr1W2-r4YwVEl4Y4Lm_vUrtqv1z7xYI_qWYgPh_94GSuJu-2H7KchGRTfvbcl8BzCkpLbC2qhDlB3cuyhWKl2iv1r3ZbiSzUurLNcEcM_CmpQguW04pKHlG-ZS4CsselqnR6eXyHmX2JmfzVfaffP__Cnmi_w1Y=002992EC"}
    )
)

model = BedrockModel(model_id="us.amazon.nova-lite-v1:0")

with streamable_http_mcp_client:
    tools = streamable_http_mcp_client.list_tools_sync()
    agent = Agent(model=model, tools=tools)
    response = agent("check my jira projects and let me know what open issues I have")
    print(response.message)
