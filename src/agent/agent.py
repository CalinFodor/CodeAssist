from agent.agent_structures import *
from agent.plan_and_solve_strategy import PlanAndSolveStrategy
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
        if strategy == AgentStrategyType.ReAct:
            return ReactStrategy(settings,tool_registry,REACT_PROMPT,10)
        elif strategy == AgentStrategyType.PlanAndSolve:
            return PlanAndSolveStrategy(settings,tool_registry)
    
    def run(self,approved:bool) -> ExecutionResult:
        return self.strategy.run(approved)
        
    