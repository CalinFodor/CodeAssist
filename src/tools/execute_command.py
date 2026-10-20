import json
import subprocess


def execute_command(args) -> str:
    if not "cmd" in args:
        return "ERROR: Please provide a list containing the command and its args to be executed"
    
    cmd = args["cmd"]
    cwd = args["cwd"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=cwd)

    try:
        o, e = proc.communicate(timeout=5.0)
    except subprocess.TimeoutExpired:
        return "ERROR: Timer for command execution expired"
    
    stdout = o.decode('utf-8')
    stderr  = e.decode('utf-8')
    exit_code = str(proc.returncode)
    
    return json.dumps({
        "stdout":stdout,
        "stderr":stderr,
        "exit_code":exit_code
    })
    
