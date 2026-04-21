"""
Public snippet: Character-based agent factory (simplified)
"""

from typing import Dict, Any
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware


class AgentFactory:
    def __init__(self, model_builder, prompt_map: Dict[str, str], tool_map: Dict[str, list]):
        self._build_model = model_builder
        self.prompt_map = prompt_map
        self.tool_map = tool_map
        self.agents: Dict[str, Any] = {}

    def build(self, character_ids: list[str]):
        for cid in character_ids:
            model = self._build_model(character_id=cid)
            tools = self.tool_map.get(cid, [])
            middleware = [
                SummarizationMiddleware(
                    model=self._build_model(summary=True),
                    trigger=("messages", 50),
                    keep=("messages", 50),
                )
            ]
            self.agents[cid] = create_agent(
                model=model,
                tools=tools or None,
                middleware=middleware,
                name=f"wave_{cid}",
            )

    def get(self, character_id: str):
        return self.agents.get(character_id)
