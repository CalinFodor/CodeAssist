from agent import agent
from tools import file_tools, tool_registry

BASE_URL ='http://192.168.192.1:11434/v1/'
API_KEY ='ollama'
MODEL = 'llama3.1:8b'
CWD = 'test_project'

if __name__ == '__main__':
    tool_reg = tool_registry.ToolRegistry()
    tool_reg.register_tool("tools/defs/read_file.json",file_tools.read_file)
    tool_reg.register_tool("tools/defs/write_to_file.json",file_tools.write_to_file)

    agent = agent.Agent(CWD,BASE_URL,API_KEY,MODEL,tool_reg)
    prompt = "Write a program to add two numbers in python in a file name add.py"
    agent.start_task(prompt)
