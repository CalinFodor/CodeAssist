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


def show_folder(dir_path:str) -> dict:
    file_map = {}
    
    dir_name = os.path.basename(dir_path)
    file_map[dir_name] = []
    
    obj = os.scandir(dir_path)
    
    for entry in obj:
        if entry.is_file():
           file_map[dir_name].append(entry.name)
        
        if entry.is_dir():
           entry_contents = show_folder(entry.path) 
           file_map[dir_name].append(entry_contents)  
    
    return file_map

def list_dir(args) -> str:
    cwd = args["cwd"]
    
    file_dict = show_folder(cwd)
    return json.dumps(file_dict)
        