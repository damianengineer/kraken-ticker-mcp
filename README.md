# Kraken Ticker MCP

> **Important Note**: This project is intended as a "Hello World" educational example to learn the Model Context Protocol (MCP). It was created for educational purposes only and is not production-ready. Use in production environments is not recommended.

> **Credits**: This project is based on and largely adapted from the [MCP Sentry Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sentry). We acknowledge and thank the original authors for their work, which we've modified to create this Kraken Ticker implementation.

## Overview

Kraken Ticker MCP is a Model Context Protocol (MCP) server for retrieving real-time ticker information from the Kraken cryptocurrency exchange API. This server provides tools for AI assistants to access up-to-date market data for various cryptocurrency trading pairs.

### Tools

1. `get_ticker`
   - Retrieve ticker information for a specific trading pair
   - Input:
     - `pair` (string): Trading pair symbol (e.g., "BTCUSD", "ETHUSD")
   - Returns: Detailed ticker information including:
     - Ask price and volume
     - Bid price and volume
     - Last trade price and volume
     - Volume statistics (today and last 24 hours)
     - Volume weighted average price
     - Number of trades
     - Low and high prices
     - Opening price

### Prompts

1. `kraken-ticker`
   - Retrieve ticker information from Kraken
   - Input:
     - `pair` (string): Trading pair symbol (e.g., "BTCUSD", "ETHUSD")
   - Returns: Formatted ticker details as conversation context

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-kraken*.

```bash
# Install uv if you don't have it
curl -sSf https://astral.sh/uv/install.sh | bash

# Run the server directly
uvx mcp-server-kraken
```

### Using PIP

Alternatively you can install `mcp-server-kraken` via pip:

```bash
pip install mcp-server-kraken
```

After installation, you can run it as a script using:

```bash
python -m mcp_server_kraken
```

## Configuration

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

<details>
<summary>Using Docker</summary>

```json
"mcpServers": {
  "kraken": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "kraken-ticker-mcp"]
  }
}
```
</details>

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "kraken": {
    "command": "uvx",
    "args": ["mcp-server-kraken"]
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"mcpServers": {
  "kraken": {
    "command": "python",
    "args": ["-m", "mcp_server_kraken"]
  }
}
```
</details>

### Usage with VS Code

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

<details>
<summary>Using Docker</summary>

```json
{
  "mcp": {
    "servers": {
      "kraken": {
        "command": "docker",
        "args": ["run", "-i", "--rm", "kraken-ticker-mcp"]
      }
    }
  }
}
```
</details>

<details>
<summary>Using uvx</summary>

```json
{
  "mcp": {
    "servers": {
      "kraken": {
        "command": "uvx",
        "args": ["mcp-server-kraken"]
      }
    }
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "mcp": {
    "servers": {
      "kraken": {
        "command": "python",
        "args": ["-m", "mcp_server_kraken"]
      }
    }
  }
}
```
</details>

### Usage with [Zed](https://github.com/zed-industries/zed)

Add to your Zed settings.json:

<details>
<summary>Using Docker</summary>

```json
"context_servers": [
  "mcp-server-kraken": {
    "command": {
      "path": "docker",
      "args": ["run", "-i", "--rm", "kraken-ticker-mcp"]
    }
  }
],
```
</details>

<details>
<summary>Using uvx</summary>

```json
"context_servers": [
  "mcp-server-kraken": {
    "command": {
      "path": "uvx",
      "args": ["mcp-server-kraken"]
    }
  }
],
```
</details>

<details>
<summary>Using pip installation</summary>

```json
"context_servers": {
  "mcp-server-kraken": {
    "command": "python",
    "args": ["-m", "mcp_server_kraken"]
  }
},
```
</details>

## Development

### Setting up the development environment

1. Clone the repository
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Testing

Run the tests with:
```bash
pytest
```

## API Reference

This MCP server uses the [Kraken Public API](https://docs.kraken.com/api/docs/rest-api/get-ticker-information) to retrieve ticker information.

## Future Work

This project is under development and has several planned improvements:

- Switching from stdio to Streamable HTTP transport for better performance and flexibility
- Containerization with Docker (after HTTP transport is implemented)
- Testing integration with Claude Desktop (currently only tested with MCP Inspector)
- Adding support for more Kraken API endpoints
- Improving error handling and response formatting

Contributions and suggestions are welcome!

## License

MIT
