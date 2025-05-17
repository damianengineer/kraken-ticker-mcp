import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

import click
import httpx
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError

KRAKEN_API_BASE = "https://api.kraken.com/0/public/"


from datetime import datetime

@dataclass
class KrakenTickerData:
    pair: str
    ask: Dict[str, str]
    bid: Dict[str, str]
    last_trade: Dict[str, str]
    volume: Dict[str, str]
    volume_weighted_avg_price: Dict[str, str]
    number_of_trades: Dict[str, str]
    low: Dict[str, str]
    high: Dict[str, str]
    opening_price: str
    timestamp: datetime = None
    source: str = "Kraken API"

    def to_text(self) -> str:
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if self.timestamp else "Unknown time"
        return f"""
Kraken Ticker Information for {self.pair}

Data retrieved from {self.source} at {timestamp_str}

Current Prices:
- Ask: {self.ask['price']} ({self.ask['whole_lot_volume']} volume, {self.ask['lot_volume']} lot volume)
- Bid: {self.bid['price']} ({self.bid['whole_lot_volume']} volume, {self.bid['lot_volume']} lot volume)
- Last Trade: {self.last_trade['price']} ({self.last_trade['volume']} volume)

Volume Statistics:
- Volume Today: {self.volume['today']}
- Volume Last 24h: {self.volume['last_24h']}
- Volume Weighted Avg Price Today: {self.volume_weighted_avg_price['today']}
- Volume Weighted Avg Price Last 24h: {self.volume_weighted_avg_price['last_24h']}

Trading Activity:
- Number of Trades Today: {self.number_of_trades['today']}
- Number of Trades Last 24h: {self.number_of_trades['last_24h']}

Price Range:
- Low Today: {self.low['today']}
- Low Last 24h: {self.low['last_24h']}
- High Today: {self.high['today']}
- High Last 24h: {self.high['last_24h']}
- Opening Price: {self.opening_price}

This data represents a snapshot of market conditions at the time of retrieval and may have changed since then.
        """

    def to_prompt_result(self) -> types.GetPromptResult:
        return types.GetPromptResult(
            description=f"Kraken Ticker Information for {self.pair}",
            messages=[
                types.PromptMessage(
                    role="user", content=types.TextContent(type="text", text=self.to_text())
                )
            ],
        )

    def to_tool_result(self) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        return [types.TextContent(type="text", text=self.to_text())]


class KrakenError(Exception):
    pass


def parse_ticker_data(pair: str, data: Dict[str, Any]) -> KrakenTickerData:
    """
    Parse the Kraken ticker API response into a structured KrakenTickerData object.
    
    The Kraken API returns ticker data in a specific format where:
    a = ask array(<price>, <whole lot volume>, <lot volume>)
    b = bid array(<price>, <whole lot volume>, <lot volume>)
    c = last trade closed array(<price>, <lot volume>)
    v = volume array(<today>, <last 24 hours>)
    p = volume weighted average price array(<today>, <last 24 hours>)
    t = number of trades array(<today>, <last 24 hours>)
    l = low array(<today>, <last 24 hours>)
    h = high array(<today>, <last 24 hours>)
    o = today's opening price
    """
    try:
        pair_data = next(iter(data.values()))
        
        return KrakenTickerData(
            pair=pair,
            ask={
                "price": pair_data["a"][0],
                "whole_lot_volume": pair_data["a"][1],
                "lot_volume": pair_data["a"][2]
            },
            bid={
                "price": pair_data["b"][0],
                "whole_lot_volume": pair_data["b"][1],
                "lot_volume": pair_data["b"][2]
            },
            last_trade={
                "price": pair_data["c"][0],
                "volume": pair_data["c"][1]
            },
            volume={
                "today": pair_data["v"][0],
                "last_24h": pair_data["v"][1]
            },
            volume_weighted_avg_price={
                "today": pair_data["p"][0],
                "last_24h": pair_data["p"][1]
            },
            number_of_trades={
                "today": pair_data["t"][0],
                "last_24h": pair_data["t"][1]
            },
            low={
                "today": pair_data["l"][0],
                "last_24h": pair_data["l"][1]
            },
            high={
                "today": pair_data["h"][0],
                "last_24h": pair_data["h"][1]
            },
            opening_price=pair_data["o"]
        )
    except (KeyError, IndexError) as e:
        raise KrakenError(f"Error parsing Kraken API response: {str(e)}")


async def get_ticker_info(
    http_client: httpx.AsyncClient, pair: str
) -> KrakenTickerData:
    """
    Fetch ticker information from the Kraken API for the specified trading pair.
    
    Args:
        http_client: An initialized httpx AsyncClient
        pair: The trading pair to get information for (e.g., "BTCUSD", "ETHUSD")
    
    Returns:
        KrakenTickerData object containing the parsed ticker information
    
    Raises:
        McpError: If there's an error fetching or parsing the data
    """
    try:
        # Kraken API uses XBT instead of BTC, handle this common case
        normalized_pair = pair.replace("BTC", "XBT")
        
        response = await http_client.get(
            f"Ticker?pair={normalized_pair}"
        )
        response.raise_for_status()
        data = response.json()
        
        if "error" in data and data["error"]:
            if data["error"]:
                raise KrakenError(f"Kraken API error: {data['error'][0]}")
        
        if "result" not in data:
            raise KrakenError("Invalid response from Kraken API: missing 'result' field")
        
        # Create ticker data with current timestamp
        ticker_data = parse_ticker_data(pair, data["result"])
        ticker_data.timestamp = datetime.utcnow()
        return ticker_data
        
    except KrakenError as e:
        raise McpError(str(e))
    except httpx.HTTPStatusError as e:
        raise McpError(f"Error fetching Kraken ticker info: {str(e)}")
    except Exception as e:
        raise McpError(f"An error occurred: {str(e)}")


# Create a FastMCP server with customizable settings
mcp = FastMCP(
    name="kraken",
    # We'll set stateless_http in the main function based on CLI args
    stateless_http=False
)

# We'll create and manage the HTTP client directly
http_client = httpx.AsyncClient(base_url=KRAKEN_API_BASE)

# Register the get_ticker prompt
@mcp.prompt(
    name="kraken-ticker",
    description="Get ticker information for a trading pair from Kraken"
)
async def kraken_ticker_prompt(pair: str):
    ticker_data = await get_ticker_info(http_client, pair)
    return ticker_data.to_prompt_result()

# Register the get_ticker tool
@mcp.tool(
    description="Get ticker information for a trading pair from Kraken"
)
async def get_ticker(pair: str) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Fetch ticker information from the Kraken API for the specified trading pair.
    
    Args:
        pair: The trading pair to get information for (e.g., "BTCUSD", "ETHUSD")
    
    Returns:
        Detailed ticker information
    """
    ticker_data = await get_ticker_info(http_client, pair)
    return ticker_data.to_tool_result()


@click.command()
@click.option("--transport", default="streamable-http", 
              type=click.Choice(["stdio", "streamable-http"]), 
              help="Transport protocol to use (stdio or streamable-http)")
@click.option("--host", default="localhost", help="Host for HTTP transport")
@click.option("--port", default=8000, type=int, help="Port for HTTP transport")
@click.option("--stateless", is_flag=True, default=False, help="Run in stateless mode")
def main(transport, host, port, stateless):
    """Run the Kraken ticker MCP server."""
    # Configure server options
    if stateless:
        mcp.stateless_http = True
        
    # Handle different transports
    if transport == "streamable-http":
        # Set host and port via environment variables
        import os
        os.environ["MCP_HOST"] = host
        os.environ["MCP_PORT"] = str(port)
        
        print(f"Starting Kraken MCP server with streamable HTTP transport")
        print(f"Server will be available at http://{host}:{port}/mcp")
        print(f"Connect your MCP Inspector to http://{host}:{port}/mcp")
    else:  # stdio
        print("Starting Kraken MCP server with stdio transport")
        print("Connect to this server using the MCP Inspector or Claude Desktop")
    
    # Run with the specified transport and mount path for streamable-http
    if transport == "streamable-http":
        mcp.run(transport=transport, mount_path="/mcp")
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    main()
