"""
Stage 2 activity: Weather Assistant.

Goal: Create an agent that uses a local MCP server (weather) and a custom tool (outfit recommendation).
Run with: python -m stages.stage2.activity.starter_agent
"""

from __future__ import annotations

import asyncio
import sys
from typing import Literal

from agents import Agent, ModelSettings, Runner, function_tool
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from pydantic import BaseModel, Field

from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model


class WeatherForecast(BaseModel):
    location: str
    temperature: float
    condition: str
    outfit_recommendation: str
    sources: list[str] = Field(
        default_factory=list, description="Data sources used (e.g. MCP, custom tool)"
    )


@function_tool
def recommend_outfit(temperature: float, condition: str) -> str:
    """
    Suggests appropriate clothing based on temperature (Celsius) and weather condition.
    """
    recommendation = []
    
    if temperature < 10:
        recommendation.append("Heavy coat, scarf, and gloves")
    elif temperature < 20:
        recommendation.append("Light jacket or sweater")
    else:
        recommendation.append("T-shirt and light trousers")

    if "rain" in condition.lower() or "drizzle" in condition.lower():
        recommendation.append("don't forget an umbrella or raincoat")
    elif "snow" in condition.lower():
        recommendation.append("wear waterproof boots")
    elif "sunny" in condition.lower() and temperature > 20:
        recommendation.append("wear sunglasses and a hat")

    return ", ".join(recommendation) + "."


# Configure the MCP server parameters to run the installed mcp_weather_server package
WEATHER_SERVER_PARAMS = MCPServerStdioParams(
    command=sys.executable,
    args=["-m", "mcp_weather_server"],
)


async def main(verbose: bool = False) -> None:
    hooks = build_verbose_hooks(verbose)
    
    # Start the MCP server as a subprocess
    async with MCPServerStdio(
        params=WEATHER_SERVER_PARAMS,
        cache_tools_list=True,
        name="Weather Server",
    ) as weather_server:
        
        weather_agent = Agent(
            name="Weather Assistant",
            instructions=(
                "You are a helpful weather assistant. "
                "1. Use the available weather MCP tool to get the forecast for the requested location. "
                "2. Use the `recommend_outfit` tool to suggest clothing based on the temperature and condition found. "
                "3. Return a structured JSON response with the forecast and recommendation."
            ),
            tools=[recommend_outfit],
            mcp_servers=[weather_server],
            model=model,
            model_settings=ModelSettings(temperature=0.0),
            output_type=WeatherForecast,
        )

        # Example query
        query = "What is the weather like in London? What should I wear?"
        print(f"Query: {query}\n")

        result = await Runner.run(weather_agent, query, hooks=hooks)
        forecast = result.final_output_as(WeatherForecast)

        print("\n=== Weather Forecast (JSON) ===")
        print(forecast.model_dump_json(indent=2))


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(main(verbose=args.verbose))