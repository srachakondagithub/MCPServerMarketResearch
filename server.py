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

@mcp.tool()
def product_portfolio(company: str) -> str:
    """Find the major products and services offered by a company."""
    response = tavily.search(
        query=f"{company} major products and services",
        max_results=3
    )
    return str(response)

@mcp.tool()
def pricing_snapshot(company: str) -> str:
    """Find current pricing information for a company's products or services."""
    response = tavily.search(
        query=f"{company} current pricing products services",
        max_results=3
    )
    return str(response)

@mcp.tool()
def recent_news_pulse(company: str) -> str:
    """Find recent news about a company."""
    response = tavily.search(
        query=f"{company} recent news",
        max_results=3
    )
    return str(response)

@mcp.prompt()
def competitor_analysis_prompt(company: str) -> str:
    """Generate a prompt for analyzing a company's competitors."""
    return f"""
    Analyze {company} and provide a structured competitive analysis.

    Include:
    1. Company overview
    2. Major competitors
    3. Major products and services
    4. Pricing information
    5. Recent news

    Provide the analysis in a clear, structured format.
    """

@mcp.resource("market://topics")
def market_topics() -> str:
    """Provide common market research topics."""
    return """
Market Research Topics:
- Company overview
- Competitors
- Product portfolio
- Pricing
- Recent news
"""

if __name__ == "__main__":
    mcp.run()