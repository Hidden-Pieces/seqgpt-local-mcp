"""General Purpose MCP Server
Tools: create_scatter_plot
Resource: hello://helper

Usage:
python server.py # stdio mode
MCP_TRANSPORT=streamable-http python server.py # http mode
"""

from __future__ import annotations
import os
import random
import tempfile
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("seqgpt-local-mcp")


@mcp.tool(title="Generate Data Table", description="Generate a data table with random values")
def generate_data_table(
    num_rows: int = 10,
    columns: list[str] | None = None,
    value_min: float = 0.0,
    value_max: float = 100.0
) -> dict:
    """
    Generate a data table with random values.
    
    Args:
        num_rows: Number of rows to generate (default: 10)
        columns: List of column names. If None, defaults to ["ID", "Value A", "Value B", "Value C"]
        value_min: Minimum value for random data (default: 0.0)
        value_max: Maximum value for random data (default: 100.0)
    
    Returns:
        Dictionary containing the table data in a structured format
    """
    if columns is None:
        columns = ["ID", "Value A", "Value B", "Value C"]
    rows = []
    for i in range(num_rows):
        row = {}
        for j, col_name in enumerate(columns):
            if j == 0 or col_name.lower() in ["id", "index", "row"]:
                row[col_name] = i + 1
            else:
                row[col_name] = round(random.uniform(value_min, value_max), 2)
        rows.append(row)
    return {
        "table_data": {
            "columns": columns,
            "rows": rows,
            "num_rows": num_rows,
            "num_columns": len(columns)
        },
        "summary": f"Generated table with {num_rows} rows and {len(columns)} columns"
    }


@mcp.resource("hello://helper", title="Hello resource")
def hello() -> str:
    return "Hello from Helper MCP! I can create scatter plots and data tables."


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()