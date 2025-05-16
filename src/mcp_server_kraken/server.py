import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

import click
import httpx
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.shared.exceptions import McpError
import mcp.server.stdio

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


async def serve() -> Server:
    """
    Create and configure the MCP server with Kraken ticker tools and prompts.
    """
    server = Server("kraken")
    http_client = httpx.AsyncClient(base_url=KRAKEN_API_BASE)

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        return [
            types.Prompt(
                name="kraken-ticker",
                description="Get ticker information for a trading pair from Kraken",
                arguments=[
                    types.PromptArgument(
                        name="pair",
                        description="Trading pair (e.g., BTCUSD, ETHUSD)",
                        required=True,
                    )
                ],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> types.GetPromptResult:
        if name != "kraken-ticker":
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or "pair" not in arguments:
            raise ValueError("Missing required argument: pair")

        pair = arguments["pair"]
        ticker_data = await get_ticker_info(http_client, pair)
        return ticker_data.to_prompt_result()

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_ticker",
                description="Get ticker information for a trading pair from Kraken",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pair": {
                            "type": "string",
                            "description": "Trading pair (e.g., BTCUSD, ETHUSD)"
                        }
                    },
                    "required": ["pair"]
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "get_ticker":
            raise ValueError(f"Unknown tool: {name}")

        if "pair" not in arguments:
            raise ValueError("Missing required argument: pair")

        pair = arguments["pair"]
        ticker_data = await get_ticker_info(http_client, pair)
        return ticker_data.to_tool_result()

    return server


@click.command()
def main():
    """Run the Kraken ticker MCP server."""
    asyncio.run(run_server())


async def run_server():
    """Initialize and run the MCP server using stdio transport."""
    server = await serve()
    
    print("Starting Kraken MCP server with stdio transport")
    print("Connect to this server using the MCP Inspector or Claude Desktop")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kraken",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(
                        tools_changed=True,
                        prompts_changed=True
                    ),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    main()
