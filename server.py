import os

from fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("MarketIntel")

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@mcp.tool()
def company_overview(company: str) -> str:
    """Get an overview of a company."""
    
    response = tavily.search(
        query=f"{company} company overview",
        max_results=3
    )

    return str(response)


@mcp.tool()
def list_competitors(company: str) -> str:
    """Find major competitors of a company."""

    response = tavily.search(
        query=f"{company} major competitors",
        max_results=3
    )

    return str(response)

if __name__ == "__main__":
    mcp.run()