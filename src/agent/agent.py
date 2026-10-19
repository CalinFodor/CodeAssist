import json
from enum import Enum

from openai import OpenAI

from tools import tool_registry


class StopReason: ...


class Done(StopReason): ...


class ApprovalNeeded(StopReason):
    def __init__(self, command: str):
        super().__init__()
        self.command = command


class AgentState(Enum):
    Idle = 1
    Holding = 2
    Executing = 3


class Agent:
    def __init__(
        self,
        cwd: str,
        url: str,
        api_key: str,
        model: str,
        tool_registry: tool_registry.ToolRegistry,
    ):
        self.client = OpenAI(base_url=url, api_key=api_key)
        self.model = model
        self.registry = tool_registry
        self.cwd = cwd
        self.messages = []
        self.state = AgentState.Idle
        self.hold_function_call = []

    def start_agent_loop(self, task: str = "") -> StopReason:
        # fresh run
        if self.state == AgentState.Idle:
            self.messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an autonomous coding assistant. Follow this execution loop strictly:\n"
                        "1. Read/inspect existing files before modifying or importing them.\n"
                        #"2. Issue exactly ONE tool call per turn. Parallel calls are forbidden.\n"
                        "2. Do not invent or assume file contents; always use actual tool outputs.\n"
                        "3. Save all code changes via write tools, never as markdown in chat.\n"
                        #"5. Always run tests for functions you modify. If the projects has tests run them if not create temporary tests by writing to a new file"
                        "4. Stop calling tools and reply in text only when the task is fully completed."
                    ),
                },
                {
                    "role": "user",
                    "content": task,
                },
            ]

            self.state = AgentState.Executing
        elif self.state == AgentState.Holding:
            self.execute_tool_call(self.hold_function_call)
            self.hold_function_call = None
            self.state = AgentState.Executing
        
        return self.execute_task()

    def execute_task(self) -> StopReason:
        while True:
            completion = self.send_prompt()
            print(completion)

            choice = completion.choices[0]
            
            print(f"{choice.message.content}")
            if choice.finish_reason != "tool_calls":
                self.state = AgentState.Idle
                return Done

            self.messages.append(choice.message)
            
            tool_call = choice.message.tool_calls[0]

            if self.registry.approval_needed(tool_call.function.name):
                self.hold_function_call = tool_call
                self.state = AgentState.Holding
                return ApprovalNeeded(tool_call.function.name)
            
            self.execute_tool_call(tool_call=tool_call)

    def execute_tool_call(self, tool_call):
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        tool_args["cwd"] = self.cwd

        task_result = self.registry.execute_tool(tool_name, tool_args)
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": task_result,
            }
        )

        self.messages.append({"role": "user", "content": "Continue"})

    def send_prompt(self):
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            tools=self.registry.schemas,
            extra_body={"options": {"num_ctx": 16384}},
        )
        return chat_completion
