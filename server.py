from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import sys
from typing import Optional, List


server_description = """This is a MCP server used for interacting with a SQLite database of my Twitter bookmarks. It allows read-only access to the database.

Important Instructions:
- At the beginning of every new conversation with the user, always call the `get_schema` tool first to understand the database structure
- Whenever possible, include the full, expanded links to any referenced Tweets/bookmarks if they're ever referenced in a response to the user.
"""

# Create the MCP server
mcp = FastMCP("SQLite Explorer", instructions=server_description)


def get_db_path():
    """Get database path from environment variable"""
    db_path = os.environ.get("DB_PATH")
    if not db_path:
        print("Error: DB_PATH environment variable must be set", file=sys.stderr)
        sys.exit(1)
    return db_path


@mcp.tool()
def get_schema() -> str:
    """Get the database schema"""
    db_path = get_db_path()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    schema = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
    return "\n".join(sql[0] for sql in schema if sql[0])


@mcp.tool()
def run_query(sql: str) -> str:
    """Execute read-only SQL queries safely."""
    db_path = get_db_path()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        result = conn.execute(sql).fetchall()
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def search_text(
    query: str,
) -> str:
    """
    Perform full-text search across bookmark_fts table. When finally presenting the results to the user, you must print out the full text of the tweet. Do not truncate the text.
    Also include the url of the tweet associated with that result so that the user can conveniently visit the actual tweet in their browser.

    Args:
        query: The search query using SQLite FTS syntax
        table_name: Optional specific FTS table to search (if None, searches all FTS tables)
        columns: Optional specific columns to return
    """
    db_path = get_db_path()
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

    try:
        results = []

        # Special handling for bookmarks with joins to get complete information
        sql = """
            WITH fts_matches AS (
                SELECT rowid, rank
                FROM bookmarks_fts
                WHERE bookmarks_fts MATCH ?
            )
            SELECT b.id,
                    b.date,
                    b.url,
                    b.text,
                    COALESCE(l.all_links, '') AS embedded_links,
                    u.name,
                    u.handle,
                    fm.rank
            FROM fts_matches fm
            JOIN bookmarks b ON b.id = fm.rowid
            JOIN users u ON b.user_id = u.id
            LEFT JOIN (
                SELECT bookmark_id, GROUP_CONCAT(expandedUrl, ' ') AS all_links
                FROM links
                GROUP BY bookmark_id
            ) l ON b.id = l.bookmark_id
            ORDER BY fm.rank
        """
        rows = conn.execute(sql, (query,)).fetchall()
        # Format results as JSON-like strings for better readability
        for row in rows:
            row_dict = {
                "id": row[0],
                "date": row[1],
                "url": row[2],
                "text": row[3],
                "embedded_links": row[4],
                "user": {"name": row[5], "handle": row[6]},
                "rank": row[7],
            }
            results.append(("bookmark", row_dict))

        return "\n".join(f"{table}: {row}" for table, row in results)

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Ensure DB_PATH is set before running
    get_db_path()
    mcp.run()
