# MCP Browser Access

## Goal
Give Claude browser access via MCP so it can navigate, scrape, interact with pages, and run performance/debugging tools.

## Status
- Config written to `/Users/macBot/Work/test/.mcp.json`
- VSCode updated — pending restart + MCP server approval

## Servers Configured

| Name | Package | Use Case |
|------|---------|----------|
| `playwright` | `@playwright/mcp@latest --browser=chrome` | General browser automation, uses installed Chrome |
| `puppeteer` | `@modelcontextprotocol/server-puppeteer` | Chrome-native, lighter weight |
| `chrome-devtools` | `chrome-devtools-mcp@latest` | DevTools access — perf traces, network, console, DOM |

## After Restart
1. VSCode should prompt to approve MCP servers from `.mcp.json` — approve all 3
2. Tell Claude: "test browser" — it will try to navigate to a URL and confirm tools are live
3. If no approval prompt appears, run `node --version && npx --version` in terminal to verify node is available

## Resources
- [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [mcp-chrome (live session extension)](https://github.com/hangwin/mcp-chrome)
- [playwright/mcp](https://github.com/microsoft/playwright-mcp)
