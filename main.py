from agent import agent as ag
from tools import file_tools, tool_registry

BASE_URL ='http://192.168.192.1:11434/v1/'
API_KEY ='ollama'
MODEL = 'qwen2.5:7b'
CWD = 'test_project'

def get_user_approval(command:str) -> bool:
    response = input(f"The Agent wants to run the following command {command}: ")
    return response.lower() == "y" or response.lower() == "yes"
       
if __name__ == '__main__':
    
    tool_reg = tool_registry.ToolRegistry()
    tool_reg.register_tool("tools/defs/read_file.json",file_tools.read_file)
    tool_reg.register_tool("tools/defs/write_to_file.json",file_tools.write_to_file)
    tool_reg.register_tool("tools/defs/list_dir.json",file_tools.list_dir)
    
    agent = ag.Agent(CWD,BASE_URL,API_KEY,MODEL,tool_reg)
    while True:
        if agent.state == ag.AgentState.Idle:
            prompt = input("Prompt the model: ")
        stop_reason = agent.start_agent_loop(prompt)
        
        if isinstance(stop_reason,ag.ApprovalNeeded) and get_user_approval(stop_reason.command):
           print("Approval granted to Agent")
           continue
        agent.state = ag.AgentState.Idle   
            
             
        
    
    
