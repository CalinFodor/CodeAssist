import agent.agent as ag
from agent.agent_structures import *
from tools import execute_command, file_tools, tool_registry

BASE_URL ='http://192.168.1.154:11434/v1/'
API_KEY ='ollama'
MODEL = 'gemma4:e4b'
CWD = '../test_project/exercism-python/exercises/practice/acronym'

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
    
    #prompt = input("Prompt the model: ")
    prompt = "One test for acronym.py is failing run pytest and fix the problem"
    settings = AgentSettings(BASE_URL,API_KEY,MODEL,CWD,prompt)
    agent = ag.Agent(settings,tool_reg,AgentStrategyType.ReAct)
    execution_result = agent.run(True)
    
    while True:
        if execution_result.stop_reason == StopReason.NeedApproval:
           execution_result = agent.run(get_user_approval(execution_result.info)) 
        else:
            break
        
    print(execution_result.info)
    
