
from openai import OpenAI

from agent.agent_data import *
from agent.react_strategy import ReactStrategy
from tools import tool_registry


class Agent:
    def __init__(
        self,
        cwd: str,
        url: str,
        api_key: str,
        model: str,
        tool_registry: tool_registry.ToolRegistry,
        mode:AgentMode
    ):
        client = OpenAI(base_url=url, api_key=api_key)
        self.strategy = self.get_strategy(client,model,mode,cwd,tool_registry)
        
    def get_strategy(self,client,model:str,mode:AgentMode,cwd:str,registry:tool_registry.ToolRegistry):
        if mode == AgentMode.ReAct:
           return ReactStrategy(client,model,cwd,registry) 
        

    def start_agent_loop(self, task: str) -> StopReason:
        # fresh run
        if self.strategy.state == AgentStatus.Idle:
            self.strategy.init_loop(task)
        elif self.strategy.state == AgentStatus.Holding:
            self.strategy.resume_hold_call()
        
        return self.strategy.loop()