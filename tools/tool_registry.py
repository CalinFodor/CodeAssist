import json
from collections.abc import Callable


class ToolRegistry:
    def __init__(self):
        self.approval_tools = []
        self.schemas = []
        self.callback_dict :dict[str,Callable[...,str]] = {}
    
    #use pydantic for schema validation later
    def register_tool(self,tool_path:str,callback:Callable[...,str],approval:bool=True):
        with open(tool_path,"r") as file:
            data = file.read() 
            
        schema = json.loads(data)
        self.schemas.append(schema)
        function_name = schema["function"]["name"]
        
        self.callback_dict[function_name] = callback
        
        if approval:
           self.approval_tools.append(function_name) 
    
    def execute_tool(self,name:str,args) -> str:
        if name not in self.callback_dict:
            return f"CALLED FUNCTION {name} DOESNT EXIST"

        return self.callback_dict[name](args)
    
    def approval_needed(self,tool_name:str) -> bool:
        return tool_name in self.approval_tools
        
