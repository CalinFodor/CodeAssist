from agent.agent_structures import *
from agent.react_strategy import ReactStrategy
from tools import tool_registry


class Agent:
    def __init__(
        self,
        settings:AgentSettings,
        tool_registry: tool_registry.ToolRegistry,
        strategy:AgentStrategyType
    ):
        self.strategy = self.set_strategy(settings,tool_registry,strategy)
    
    def set_strategy(self,settings:AgentSettings,tool_registry:tool_registry.ToolRegistry,strategy:AgentStrategyType) -> AgentStrategy:
        return ReactStrategy(settings,tool_registry)
    
    def run(self,approved:bool) -> ExecutionResult:
        return self.strategy.run(approved)
        
    