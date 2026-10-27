import json

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageFunctionToolCall,
    ChatCompletionMessageParam,
)

from agent.agent_structures import *
from tools import tool_registry


class ReactStrategy(AgentStrategy):
    def __init__(self,settings:AgentSettings,tools:tool_registry.ToolRegistry,system_prompt:str,max_iterations:int):
        self.cwd = settings.cwd
        self.client = settings.client
        self.model = settings.model
        self.registry = tools
        self.tools_to_approve:list[ChatCompletionMessageFunctionToolCall] = []
        
        self.max_iterations = max_iterations
        self.iterations = 0
        self.messages:list[ChatCompletionMessageParam] = []
        self.task = settings.task
        self.init_messages(system_prompt)
        self.state = AgentState.Executing

    def init_messages(self,system_prompt:str):
        self.messages = [
                {
                    "role": "system",
                    "content":system_prompt,
                },
                {
                    "role": "user",
                    "content": self.task,
               },
            ]
    
    def run(self,approved:bool) -> ExecutionResult:
        if self.state == AgentState.WaitingForApproval:
            self.__resume(approved)
        
        while self.iterations < self.max_iterations:
            completion = self.send_react_prompt()

            choice = completion.choices[0]
            
            if choice.message.content != "":
                print(f"{choice.message.content}")
            
            print(f"Total tokens:{completion.usage.total_tokens}")
            
            if choice.finish_reason != "tool_calls":
                print(choice.message.content)
                return ExecutionResult(StopReason.TaskFinished,choice.message.content)

            self.messages.append(choice.message)
            
            for tool in choice.message.tool_calls:
                if self.registry.approval_needed(tool.function.name):
                    self.tools_to_approve.append(tool)
                else:
                    self.execute_tool_call(tool_call=tool)
            
            if len(self.tools_to_approve) != 0:
               info = ""
               for tool in self.tools_to_approve:
                   info += f"{tool.function.name}-{tool.function.arguments}\n" 
               self.state = AgentState.WaitingForApproval
               return ExecutionResult(StopReason.NeedApproval,info) 
            
            self.iterations += 1
        return ExecutionResult(StopReason.MaxIterations,"Reached max iterations")
    
    def send_react_prompt(self) -> ChatCompletion:
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model=self.model,
                tools=self.registry.schemas, # type: ignore
                extra_body={
                    "options": {
                        "num_ctx": 8192  # Adjust context window (e.g., 8192, 16384, 32768)
                    },
                    "think":False
                }
            )
            return chat_completion 
   
    def execute_tool_call(self, tool_call:ChatCompletionMessageFunctionToolCall):
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        tool_args["cwd"] = self.cwd

        print(f"Running {tool_registry.tool_print_form(tool_name,tool_args)}...")
        
        task_result = self.registry.execute_tool(tool_name, tool_args)
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": task_result,
            }
        )


    def __resume(self,approved:bool):
        for tool_call in self.tools_to_approve:
            if approved:
                self.execute_tool_call(tool_call)
            else:
                self.messages.append({
                     "role": "tool",
                      "tool_call_id": tool_call.id,
                      "content": "USER Denied this tool call"
                })
                
        self.tools_to_approve = []
        self.state = AgentState.Executing