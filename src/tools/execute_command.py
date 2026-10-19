import subprocess


def execute_command(args):
    if not "cmd" in args:
        return "Please provide a list containing the command and its args to be executed"
    
    cmd = args["cmd"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    o, e = proc.communicate(timeout=5.0)

    stdout = o.decode('ascii')
    stderr  = e.decode('ascii')
    exit_code = str(proc.returncode)
    
    return {
        "stdout":stdout,
        "stderr":stderr,
        "exit_code":exit_code
    }
    
