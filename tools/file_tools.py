import os


def read_file(args) -> str:
    if "file_name" not in args:
        return "Incorrect usage: expected argument of name file_name"
    
    file_name = args["file_name"]
    if not os.path.exists(file_name):
        return f"File {file_name} does not exist"
    
    with open(file_name,"r") as file:
        return file.read()

def write_to_file(args) -> str:
    if "file_name" not in args or "content" not in args:
        return "Incorrect usage: expected arguments file_name and content"
    
    file_name = args["file_name"]
    content = args["content"]
    
    with open(file_name,"w") as file:
        file.write(content)
    return "Written to file succesfully"
