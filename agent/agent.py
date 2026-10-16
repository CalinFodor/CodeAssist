import json

from openai import OpenAI

from tools import tool_registry


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

    def start_task(self, task: str):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an autonomous coding assistant. Follow this execution loop strictly:\n"
                    "1. Read/inspect existing files before modifying or importing them.\n"
                    "2. Issue exactly ONE tool call per turn. Parallel calls are forbidden.\n"
                    "3. Do not invent or assume file contents; always use actual tool outputs.\n"
                    "4. Save all code changes via write tools, never as markdown in chat.\n"
                    "5. Stop calling tools and reply in text only when the task is fully completed."
                )
            },
            {
                "role": "user",
                "content": task,
            },
        ]

        while True:
            completion = self.send_prompt(messages)
            print(completion)

            choice = completion.choices[0]
            if choice.finish_reason != "tool_calls":
                print(f"{choice.message.content}")
                return

            messages.append(choice.message)

            tool_call = choice.message.tool_calls[0]
            task_result = self.execute_tool_call(tool_call.function)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": task_result,
                }
            )
            
            messages.append(
                {
                    "role":"user",
                    "content":"Continue"
                }
            )

    def execute_tool_call(self, tool_call) -> str:
        tool_name = tool_call.name
        tool_args = json.loads(tool_call.arguments)
        tool_args["cwd"] = self.cwd

        return self.registry.execute_tool(tool_name, tool_args)

    def send_prompt(self, history):
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=self.model,
            tools=self.registry.schemas,
            extra_body={"options": {"num_ctx": 16384}},
        )
        return chat_completion
