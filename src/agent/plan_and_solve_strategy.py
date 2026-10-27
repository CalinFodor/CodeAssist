import json

from pydantic import BaseModel

from agent.agent_structures import *
from agent.react_strategy import ReactStrategy
from tools import tool_registry


class PlanStep(BaseModel):
    objective:str
    file:str
    details:str

class CodingPlan(BaseModel):
    summary:str
    target_files:list[str]
    steps:list[str]
    verification_command:str

class PlanAndSolveStrategy(AgentStrategy):
    def __init__(self,settings:AgentSettings,tools:tool_registry.ToolRegistry):
        self.settings = settings
        self.tools = tools
        
        self.state = AgentState.Exploring
        
        self.react_strategy = None
        self.exploration:str | None = None
        self.plan:CodingPlan | None = None
        self.get_curr_strategy()
    
    def get_curr_strategy(self):
        if self.state == AgentState.Exploring:
           self.react_strategy = ReactStrategy(self.settings,self.tools,EXPLORER_PROMPT,5) 
            
    def run(self,approved:bool) -> ExecutionResult:
        if self.state == AgentState.Exploring:
            print("Exploring...")
            execution_result = self.react_strategy.run(approved)
            
            if execution_result.stop_reason == StopReason.NeedApproval:
                return execution_result
            elif execution_result.stop_reason == StopReason.TaskFinished:
                self.exploration = execution_result.info
                self.__next_state()
            else:
                raise RuntimeError("Explorer did not finish in time")
        else:
            self.__plan()
            plan_str = json.dumps(self.plan)
            return ExecutionResult(StopReason.TaskFinished,plan_str)
            
    def __next_state(self):
        if self.state == AgentState.Exploring:
           self.state = AgentState.Planning 
           
    def __plan(self):
        planner_messages = [
            {
                "role":"system",
                "content":PLANNER_PROMPT
            },
            {
                "role":"user",
                "content":self.exploration
            }
        ]
        
        completion = self.settings.client.chat.completions.create(
            messages=planner_messages,
            model=self.settings.model,
            response_format=CodingPlan
        )
        
        self.plan = completion.choices[0].message.parsed
