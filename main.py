from agent import agent
from tools import file_tools, tool_registry

BASE_URL ='http://192.168.192.1:11434/v1/'
API_KEY ='ollama'
MODEL = 'llama3.1:8b'

tool_reg = tool_registry.ToolRegistry()
tool_reg.register_tool("tools/defs/read_file.json",file_tools.read_file)

agent = agent.Agent(BASE_URL,API_KEY,MODEL,tool_reg)
while True:
    prompt = input("Write something for llm: ")
    agent.start_task(prompt)
