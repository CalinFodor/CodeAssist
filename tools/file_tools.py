import os


def read_file(file_name:str) -> str:
    if not os.path.exists(file_name):
        return f"File {file_name} does not exist"
    
    with open(file_name,"r") as file:
        return file.read()

