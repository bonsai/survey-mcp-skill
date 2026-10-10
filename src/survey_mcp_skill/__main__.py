"""CLI entry: stdio MCP or HTTP server."""

import argparse

from .server import app, mcp


def main():
    parser = argparse.ArgumentParser(description="Survey MCP Skill")
    parser.add_argument(
        "transport",
        nargs="?",
        default="stdio",
        choices=["stdio", "http", "sse"],
        help="Transport type (stdio for Pi, http/sse for browser)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio", show_banner=False)
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port, show_banner=False)


if __name__ == "__main__":
    main()
