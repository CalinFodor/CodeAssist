from agent import agent as ag
from agent import agent_data
from tools import execute_command, file_tools, tool_registry

BASE_URL ='http://192.168.1.154:11434/v1/'
API_KEY ='ollama'
MODEL = 'qwen2.5:7b'
CWD = '../test_project/exercism-python/exercises/practice/accumulate'

def get_user_approval(command:str) -> bool:
    response = input(f"The Agent wants to run the following command {command}: ")
    return response.lower() == "y" or response.lower() == "yes"
       
if __name__ == '__main__':
    
    tool_reg = tool_registry.ToolRegistry()
    tool_reg.register_tool("tools/defs/read_file.json",file_tools.read_file,False)
    tool_reg.register_tool("tools/defs/create_file.json",file_tools.write_file)
    tool_reg.register_tool("tools/defs/list_dir.json",file_tools.list_dir,False)
    tool_reg.register_tool("tools/defs/edit_file.json",file_tools.edit_file)
    tool_reg.register_tool("tools/defs/execute_command.json",execute_command.execute_command)
    
    agent = ag.Agent(CWD,BASE_URL,API_KEY,MODEL,tool_reg,agent_data.AgentMode.ReAct)
    while True:
        if agent.strategy.state == ag.AgentStatus.Idle:
            prompt = input("Prompt the model: ")
        stop_reason = agent.start_agent_loop(prompt)
        
        if isinstance(stop_reason,ag.ApprovalNeeded) and get_user_approval(stop_reason.command):
           print("Approval granted to Agent")
           continue
        agent.strategy.state = ag.AgentStatus.Idle   

    
    
