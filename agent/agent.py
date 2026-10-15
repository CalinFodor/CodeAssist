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
                "role": "user",
                "content": task,
            }
        ]
        
       completion = self.send_prompt(messages)
       print(completion)
    
    
    def send_prompt(self,history):
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=self.model,
            tools = self.registry.schemas,
        )
        return chat_completion
        
        
        
        
        
        
