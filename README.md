# Twitter Bookmarks MCP

⚠️ This project is still very much a work in progress. Expect rough edges and significant changes. Feel free to open issues or reach out on twitter @626ripes if you encounter any problems.

This is a MCP server for providing Claude and other AI assitants access to your Twitter bookmarks in the form of a SQLite database so you can search, analyze, chat with, and generate visualizations of them directly in clients like Claude Desktop.

It's a companion for my [Twitter Boomark Search](https://www.twitter-bookmark-search.com/) app.

## Available Tools

This MCP server is a fairly simple and thin interface layer over a read-only sqlite datbase. It has the below simple tools

- `get_schema()`: Returns the database schema. This is called at the start of each conversation to understand the database structure.
- `run_query(sql)`: Executes read-only SQL queries.
- `search_text(query)`: Performs full-text search on the database's fts index. Returns complete tweet information including text, URLs, user details, and embedded links.

## Setup

### Prerequisites

- Make sure you have the sqlite database file of your bookmarks. To do so, first extract your bookmarks in json format by following the steps [here](https://twitter-bookmark-search.com) and upload them in that same page. Then go to the [claude-plugin](https://twitter-bookmark-search.com/claude-plugin) page to convert them to a sqlite database for you to download to your computer. Take note of the filepath of this saved sqlite file.
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/chrislee973/twitter-bookmarks-mcp
   cd twitter-bookmarks-mcp
   ```

2. Install dependencies:

   ```bash
   uv venv && uv pip install -r pyproject.toml
   ```

## Connecting to Claude Desktop

1. Run the command:

```bash
uv run mcp install -e . server.py -v DB_PATH=path/to/db
```

Replace `path/to/db` with the full path to wherever your database file is saved.

2. Restart Claude Desktop

3. Try asking Claude questions like:
   - "Return the abstracts of my 5 most recent bookmarked arxiv papers"
   - "Look through my twitter bookmarks for bookmarks that contain a link to the blog lesswrong, and summarize the content of each of those blog posts"
   - "Create a chart of my bookmark frequency over time"
