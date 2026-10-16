from agent import agent
from tools import file_tools, tool_registry

BASE_URL ='http://192.168.192.1:11434/v1/'
API_KEY ='ollama'
MODEL = 'qwen2.5:7b'
CWD = 'test_project'

if __name__ == '__main__':
    
    tool_reg = tool_registry.ToolRegistry()
    tool_reg.register_tool("tools/defs/read_file.json",file_tools.read_file)
    tool_reg.register_tool("tools/defs/write_to_file.json",file_tools.write_to_file)
    tool_reg.register_tool("tools/defs/list_dir.json",file_tools.list_dir)
    
    agent = agent.Agent(CWD,BASE_URL,API_KEY,MODEL,tool_reg)
    while True:
        prompt = input("Prompt the model: ")
        agent.start_task(prompt)
    
    
