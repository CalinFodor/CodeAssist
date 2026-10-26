import json
from collections.abc import Callable


# this doesnt fit but i dont know where to put it yet
def tool_print_form(name: str, tool_args:dict[str,str]) -> str:
    arg_list:list[str] = []
    for param, arg in tool_args.items():
        if param != "cwd":
            arg_list.append(f"{param}:{arg}")

    return f"{name}({', '.join(arg_list)})"

    

class ToolRegistry:
    def __init__(self):
        self.approval_tools = []
        self.schemas = []
        self.callback_dict: dict[str, Callable[..., str]] = {}

    # use pydantic for schema validation later
    def register_tool(
        self, tool_path: str, callback: Callable[..., str], approval: bool = True
    ):
        with open(tool_path, "r") as file:
            data = file.read()

        schema = json.loads(data)
        self.schemas.append(schema)
        function_name = schema["function"]["name"]

        self.callback_dict[function_name] = callback

        if approval:
            self.approval_tools.append(function_name)

    def execute_tool(self, name: str, args:list[dict[str,str]]) -> str:
        if name not in self.callback_dict:
            return f"CALLED FUNCTION {name} DOESNT EXIST"

        result = self.callback_dict[name](args)
        print(f"Result: {result}")
        return result

    def approval_needed(self, tool_name: str) -> bool:
        return tool_name in self.approval_tools
