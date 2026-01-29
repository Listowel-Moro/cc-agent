"""
Test script to verify the enhanced agent with http_request and generate_image tools
"""
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import http_request, generate_image
from datetime import datetime
import os

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


# Configure the agent with tools
model = BedrockModel(model_id="us.amazon.nova-lite-v1:0")

agent = Agent(
    model=model,
    tools=[
        get_current_datetime,
        calculate,
        http_request,
        generate_image
    ]
)

print("Testing Enhanced Strands Agent")
print("=" * 50)

# Test 1: Basic datetime tool
print("\n[TEST 1] Testing get_current_datetime...")
try:
    response = agent("What is the current date and time?")
    print(f"[OK] Success: {response}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

# Test 2: Calculator tool
print("\n[TEST 2] Testing calculate...")
try:
    response = agent("Calculate 25 * 4 + 10")
    print(f"[OK] Success: {response}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

# Test 3: HTTP request tool
print("\n[TEST 3] Testing http_request...")
try:
    response = agent("Make a GET request to https://api.github.com/zen")
    print(f"[OK] Success: {response}")
except Exception as e:
    print(f"[FAIL] Failed: {e}")

print("\n" + "=" * 50)
print("Testing complete!")
print("\nNote: generate_image tool requires AWS Bedrock configuration")
print("and will be tested separately with proper credentials.")
