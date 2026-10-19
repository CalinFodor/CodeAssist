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

def write_file(args) -> str:
    if "file_name" not in args:
        return "Incorrect usage: expected arguments file_name"
    
    file_name = args["file_name"]
    cwd = args["cwd"]
    
    file_path = os.path.join(cwd,file_name)
    
    try:
        with open(file_path,"x"):
            return "File created"
    except FileExistsError:
        return "File already exists"
   

def show_folder(dir_path:str,depth:int,prefix:str,max_depth:int=3,max_files_per_dir=25) -> str:
    
    dir_name = os.path.basename(dir_path)
    result = f"{dir_name}/"
    
    if depth > max_depth:
        return result + "\n"
        
    obj = os.scandir(dir_path)
    
    folder_contents = [entry for entry in obj]
    
    no_entries = len(folder_contents)
    
    entries = [result]
    
    for index,entry in enumerate(folder_contents):
        connector = "├──"
        if index > no_entries:
            connector = "└──"
        
        if index > max_files_per_dir - 1 and depth != 1:
           connector = "└──"
           entries.append(f"{prefix}{connector}...[TRUNCATED] ({len(folder_contents) - max_files_per_dir} ommited) Target this folder to see all contents")
           break 
                
        if entry.is_file() or depth > max_depth:
           entries.append(f"{prefix}{connector}{entry.name}")
        
        if entry.is_dir():
           new_prefix = depth*"| "
           entry_contents = show_folder(entry.path,depth+1,new_prefix) 
           entries.append(f"{prefix}{connector}{entry_contents}")  
    
    return "\n".join(entries)
    
    
def list_dir(args) -> str:
    cwd = args["cwd"]
    full_path = cwd
    
    max_depth = 5
    depth = 3
    if "depth" in args and args["depth"] <= max_depth:
        depth = args["depth"]
    
    if "dir_name" in args:
        dir = args["dir_name"]
        full_path = os.path.join(cwd,dir)
    
    return show_folder(full_path,1,"",max_depth=depth)
    
    
        