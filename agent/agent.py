import json

from openai import OpenAI

from tools import tool_registry


class Agent:
    def __init__(self, url: str, api_key: str,model:str, tool_registry:tool_registry.ToolRegistry):
        self.client = OpenAI(base_url=url, api_key=api_key)
        self.model = model
        self.registry = tool_registry

    def start_task(self,task:str):
       messages =  [
           {
             "role":"system",
             "content":"""
                You have access to tools. When you decide to call a tool, call the function directly.
                Do NOT explain your plan or output JSON inside conversational text.
                When you receive confirmation the task is completed dont call any other tools.
             """  
           },
            {
                "role": "user",
                "content": task,
            }
        ]
       
       while True:
            completion = self.send_prompt(messages)
            print(completion)
            choice = completion.choices[0]
            
            if choice.finish_reason != 'tool_calls':
                print("Task completed")
                break
            
            tool_call = choice.message.tool_calls[0]
            task_result = self.execute_tool_call(tool_call.function)
            messages.append(
                {
                    "role":"tool",
                    "tool_call_id":tool_call.id,
                    "name":tool_call.function.name,
                    "content":task_result
                }
            )
            
            
            
                
    def execute_tool_call(self,tool_call) -> str:  
        tool_name = tool_call.name
        tool_args = json.loads(tool_call.arguments)
        
        return self.registry.execute_tool(tool_name,tool_args)
    
    def send_prompt(self,history):
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=self.model,
            tools = self.registry.schemas,
        )
        return chat_completion
        
        
        
        
        
        
