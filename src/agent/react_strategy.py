import json

from agent.agent_data import *
from tools import tool_registry


class ReactStrategy:
    def __init__(self,client,model,cwd,tools:tool_registry.ToolRegistry):
        self.cwd = cwd
        self.tools = tools
        self.messages = []
        self.client = client
        self.model = model
        self.registry = tools
        self.state = AgentStatus.Idle
        self.hold_function_call = None
    
    def init_loop(self,task:str):
        self.messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": task,
               },
            ]
        self.state = AgentStatus.Executing
    
    def loop(self) -> StopReason:
        while True:
            completion = self.send_react_prompt()

            choice = completion.choices[0]
            
            if choice.message.content != "":
                print(f"{choice.message.content}")
            
            print(f"Total tokens:{completion.usage.total_tokens}")
            
            if choice.finish_reason != "tool_calls":
                self.state = AgentStatus.Idle
                return Done

            
            tool_call = choice.message.tool_calls[0]
            self.messages.append(choice.message)

            if self.registry.approval_needed(tool_call.function.name):
                self.hold_function_call = tool_call
                self.state = AgentStatus.Holding
                
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                return ApprovalNeeded(tool_registry.tool_print_form(tool_name,tool_args))
            
            self.execute_tool_call(tool_call=tool_call)
        
    
    def execute_tool_call(self, tool_call):
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


    def send_react_prompt(self):
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            tools=self.registry.schemas,
            extra_body={"options": {"num_ctx": 16384}},
            parallel_tool_calls=False
        )
        return chat_completion     
    
    def resume_hold_call(self):
        self.execute_tool_call(self.hold_function_call)
        self.hold_function_call = None
        self.state = AgentStatus.Executing