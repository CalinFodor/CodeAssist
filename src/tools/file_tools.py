import os


def read_file(args:dict[str,str]) -> str:
    if "file_name" not in args:
        return "ERROR: Incorrect usage: expected argument of name file_name"
    
    file_name = args["file_name"]
    cwd = args["cwd"]
    file_path = os.path.join(cwd,file_name)
    
    try:
        with open(file_path,"r") as file:
            return file.read()
    except FileNotFoundError:
        return f"ERROR: File {file_name} does not exist"


def write_file(args:dict[str,str]) -> str:
    if "file_name" not in args or "content" not in args:
        return "ERROR: Incorrect usage: expected arguments file_name"
    
    file_name = args["file_name"]
    content = args["content"] 
    cwd = args["cwd"]
    
    file_path = os.path.join(cwd,file_name)
    
    try:
        with open(file_path,"x") as file, open(file_path,"w") as file:
            file.write(content)
        return f"File {file_name} created sucessfully"
    except FileExistsError:
        return f"File {file_name} already exists"
    except OSError as e:
        return f"ERROR: {e}"
    
def edit_file(args:dict[str,str]) -> str:
    if "file_name" not in args:
        return "ERROR: Incorrect usage: expected arguments file_name"
    print(args)
    file_name = args["file_name"]
    old_str = args["old_str"]
    new_str = args["new_str"]
    cwd = args["cwd"]
    
    file_path = os.path.join(cwd,file_name)
    
    if old_str == "":
        return "ERROR: Please provide a value for old_str"
    
    try:
        with open(file_path,"r") as file:
            data = file.read()
            
        if old_str not in data:
            return "ERROR: old_str not found in file"    
        
        data = data.replace(old_str,new_str)
        
        with open(file_path,"w") as file:
            file.write(data)
        return f"File {file_name} edited"
    except FileNotFoundError:
        return "ERROR: File does not exist"   
    except OSError as e:
        return f"ERROR {e}"
    
def show_folder(dir_path:str,cwd:str,depth:int,prefix:str,max_depth:int=3,max_files_per_dir:int=25) -> str:
    
    dir_name = os.path.basename(dir_path)
    if dir_name == cwd and depth == 1:
       dir_name = '.' 
    
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
        
        if entry.is_dir() and not entry.name.startswith('.') and not entry.name in IGNORE_FOLDERS:
           new_prefix = depth*"| "
           entry_contents = show_folder(entry.path,cwd,depth+1,new_prefix) 
           entries.append(f"{prefix}{connector}{entry_contents}")  
    
    return "\n".join(entries)
    
IGNORE_FOLDERS = ['__pycache__','node_modules']

def list_dir(args:dict[str,str]) -> str:
    cwd = args["cwd"]
    full_path = cwd
    
    max_depth = 5
    depth = 3
    if "depth" in args and int(args["depth"]) <= max_depth:
        depth = int(args["depth"])
    
    if "dir_name" in args:
        dir = args["dir_name"]
        full_path = os.path.join(cwd,dir)
    
    cwd_name = os.path.basename(cwd)
    return show_folder(full_path,cwd_name,1,"",max_depth=depth)
    
    
        