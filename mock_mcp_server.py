import json
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("My First MCP Server")

@mcp.tool()
def add_numbers(a: int, b: int) -> str:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    result = a + b
    return json.dumps({
        "result": result,
        "calculation": f"{a} + {b} = {result}"
    })

# Run the server
if __name__ == "__main__":
    mcp.run()