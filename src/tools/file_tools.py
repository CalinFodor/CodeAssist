import json
import os


def read_file(args) -> str:
    if "file_name" not in args:
        return "Incorrect usage: expected argument of name file_name"
    
    file_name = args["file_name"]
    cwd = args["cwd"]
    file_path = os.path.join(cwd,file_name)
    
    if not os.path.exists(file_path):
        return f"File {file_name} does not exist"
    
    with open(file_path,"r") as file:
        return file.read()

def write_to_file(args) -> str:
    if "file_name" not in args or "content" not in args:
        return "Incorrect usage: expected arguments file_name and content"
    
    file_name = args["file_name"]
    content = args["content"]
    cwd = args["cwd"]
    
    file_path = os.path.join(cwd,file_name)
    
    with open(file_path,"w",encoding='utf-8') as file:
        file.write(content)
    return "Written to file succesfully"


def show_folder(dir_path:str,depth:int,prefix:str,max_depth:int=3,max_files_per_dir=2) -> str:
    
    dir_name = os.path.basename(dir_path)
    result = f"{dir_name}/\n"
    
    obj = os.scandir(dir_path)
    
    folder_contents = [entry for entry in obj]
    no_entries = len(folder_contents)
    
    entries = []
    
    for index,entry in enumerate(folder_contents):
    
        connector = "├──"
        if index > no_entries:
            connector = "└──"
        
        if index > max_files_per_dir - 1:
           connector = "└──"
           entries.append(f"{prefix}{connector}...[TRUNCATED Use a glob pattern to find more files]")
           break 
                
        if entry.is_file() or depth > max_depth:
           entries.append(f"{prefix}{connector}{entry.name}")
        
        if entry.is_dir():
           entry_contents = show_folder(entry.path,depth+1,prefix+"  ") 
           entries.append(f"{prefix}{connector}{entry_contents}")  
    
    return result + "\n".join(entries)
    
    
def list_dir(args,dir:str,depth:int) -> str:
    cwd = args["cwd"]
    
    full_path = os.path.join(cwd,dir)
    
    file_dict = show_folder(full_path,depth)
        