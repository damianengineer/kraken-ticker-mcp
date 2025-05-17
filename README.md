# Kraken Ticker MCP

> **Important Note**: This project is intended as a "Hello World" educational example to learn the Model Context Protocol (MCP). It was created for educational purposes only and is not production-ready. Use in production environments is not recommended.

## Credits

This implementation was developed according to the following specifications and resources:

- [**Model Context Protocol (MCP) Specification**](https://github.com/modelcontextprotocol/protocol) - The official protocol specification defining the standard interface for tool calling.

- [**MCP Python SDK**](https://github.com/modelcontextprotocol/python-sdk) - The Python implementation of the MCP protocol used in this project.

- [MCP Sentry Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sentry) - Used as a reference implementation during early development.

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

## Quickstart

The recommended way to use Kraken Ticker MCP is through Docker containerization. This provides a consistent environment and simplifies deployment.

```bash
# Clone the repository
git clone https://github.com/your-username/kraken-ticker-mcp.git
cd kraken-ticker-mcp

# Build the Docker image
docker build -t kraken-ticker-mcp .

# Run the container with port forwarding
docker run -d -p 8000:8000 --name kraken-mcp-server kraken-ticker-mcp

# Check that the container is running
docker ps | grep kraken-mcp-server
```

That's it! Your MCP server is now running with streamable HTTP transport on port 8000, ready to be accessed at `http://localhost:8000/mcp`.

## Deployment and Usage

### Containerized Deployment (Recommended)

The most reliable way to use the Kraken Ticker MCP server is through Docker container deployment:

```bash
# Build the Docker image
docker build -t kraken-ticker-mcp .

# Run the container with port forwarding
docker run -d -p 8000:8000 --name kraken-mcp-server kraken-ticker-mcp
```

This will:
1. Build a Docker image with all dependencies installed
2. Run the server in a container with streamable HTTP transport
3. Map container port 8000 to host port 8000 for access
4. Mount the MCP endpoint at `/mcp` in accordance with the MCP specification

### Connecting with MCP Inspector

The easiest way to test the server is using the MCP Inspector tool:

```bash
# Launch the MCP Inspector
npx @modelcontextprotocol/inspector
```

Then:
1. Browse to http://127.0.0.1:6274/
2. Connect to http://127.0.0.1:8000/mcp
3. Use the `get_ticker` tool with a cryptocurrency pair like "BTCUSD"

![MCP Inspector Connection](Inspector.png)

### Command Line Options

The server supports the following command line options:

```bash
# Show help
python -m mcp_server_kraken --help

# Available options:
--transport [stdio|streamable-http]  # Transport protocol (default: streamable-http)
--host TEXT                          # Host for HTTP transport (default: localhost)
--port INTEGER                       # Port for HTTP transport (default: 8000)
--stateless                          # Run in stateless mode for better scalability
```

## Untested Methods

The following integration methods are provided but have not been verified in the current implementation:

| Client | Transport | Configuration Method | Status |
|--------|-----------|----------------------|--------|
| Claude Desktop | stdio | `claude_desktop_config.json` | Untested |
| VS Code | stdio | User Settings (JSON) | Untested |
| Windsurf | streamable-http | `mcp_config.json` | Untested |
| Custom MCP Clients | streamable-http | Connect to http://localhost:8000/mcp | Untested |

### Usage with Claude Desktop (Untested)

Add this to your `claude_desktop_config.json`:

<details>
<summary>Using Docker</summary>

```json
"mcpServers": {
  "kraken": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "kraken-ticker-mcp", "--transport", "stdio"]
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
    "args": ["mcp-server-kraken", "--transport", "stdio"]
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
    "args": ["-m", "mcp_server_kraken", "--transport", "stdio"]
  }
}
```
</details>

### Usage with VS Code (Untested)

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
        "args": ["run", "-i", "--rm", "kraken-ticker-mcp", "--transport", "stdio"]
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
        "args": ["mcp-server-kraken", "--transport", "stdio"]
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
        "args": ["-m", "mcp_server_kraken", "--transport", "stdio"]
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
3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## License

The Kraken Ticker MCP server is released under the MIT License, which is a permissive license that provides maximum freedom to use the code with minimal restrictions.

```
MIT License

Copyright (c) 2025 Kraken Ticker MCP Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Security Policy

If you discover a security vulnerability, privacy concern, or bug, please report it to:

fixit [dot] github [at] attentiontransformer [dot] com

Issues will be addressed on a best-effort basis. We appreciate your help in making this project more secure.

### Testing

Run the tests with:
```bash
pytest
```

## API Reference

This MCP server uses the [Kraken Public API](https://docs.kraken.com/api/docs/rest-api/get-ticker-information) to retrieve ticker information.

### Connecting to Streamable HTTP Server

To connect to the server using streamable HTTP:

1. **Using MCP Inspector**:
   ```bash
   mcp inspect http://localhost:8000/mcp
   ```

2. **Using Custom Clients**:
   - Send HTTP POST requests to `http://localhost:8000/mcp` with JSON-RPC messages
   - Receive responses as SSE streams or JSON objects

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
