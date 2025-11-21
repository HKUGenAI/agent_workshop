# Stage 2 · Custom Tools & MCP

Time to augment the base agent with bespoke capabilities. You will create a structured `FunctionTool`, wire in a local MCP (Model Context Protocol) server, and expose both to the agent runtime.

## Learning Goals

- Design custom tools using `@function_tool` and strict docstrings.
- Connect to an existing MCP server (`mcp_weather_server`) via stdio.
- Combine multiple capabilities (custom logic + external data) within a single agent run.
- Observe tool call traces with verbose logging.

## 1. Prerequisites

Carry over the Docker environment from Stage 1:

```bash
docker compose up -d
docker compose exec workshop bash
```

### Helpful environment flags

- `OPENAI_BASE_URL=http://ollama:11434/v1`
- `OPENAI_API_KEY=ollama`

You can enable verbose tool tracing while experimenting:

```bash
export AGENTS_LOG_LEVEL=DEBUG
```

## 2. Custom Function Tools

Key imports:

- `from agents import function_tool`
- `@function_tool` decorator automatically derives JSON schemas from type hints and docstrings.
- Return values can be plain Python primitives or Pydantic models.

### Example Walkthrough

Open `stages/stage2/demo.py`. It defines:

1. A custom tool helper.
2. An MCP server connection (using a local example or external package).
3. An agent that combines capabilities.

Run it as a module from the repo root:

```bash
python -m stages.stage2.demo
```

## 3. Using an MCP Server

In this stage, we use the `mcp_weather_server` package to provide real-time weather data. This demonstrates how to leverage the growing ecosystem of MCP servers.

To connect to an MCP server via stdio, we use `MCPServerStdio` and point it to the executable command.

```python
from agents.mcp import MCPServerStdio, MCPServerStdioParams
import sys

params = MCPServerStdioParams(
    command=sys.executable,
    args=["-m", "mcp_weather_server"],
)
```

## 4. Activity

File: `stages/stage2/activity/starter_agent.py`

> Build a "Weather Assistant" agent that:
>
> 1. Fetches weather data using the `mcp_weather_server`.
> 2. Uses a custom tool `recommend_outfit` to generate clothing suggestions based on the temperature and condition.
> 3. Returns a structured JSON report.
>
> The starter script has been set up with the necessary imports and a skeleton. Your tasks are to:
>
> - Review the `recommend_outfit` tool logic.
> - Ensure the agent instructions coordinate the tool calls (Weather MCP -> Custom Tool -> Final Answer).
> - Run the agent and verify the output.

Run the activity:

```bash
python -m stages.stage2.activity.starter_agent
```

Use `--verbose` to see the agent discovering and calling the tools:

```bash
python -m stages.stage2.activity.starter_agent --verbose
```

You should see the agent call the weather tool, then your outfit tool, and finally produce the JSON.

**Stretch ideas**

- Add a `CityGuide` tool that suggests places to visit based on the weather.
- Swap the model to a different one (if available) and see how it handles tool calling.
- Add error handling if the city is not found.

Once you can orchestrate custom tools and MCP data, move on to Stage 3 to coordinate entire multi-agent workflows.