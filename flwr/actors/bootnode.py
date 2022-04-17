import subprocess
from pathlib import Path

def run_cmd(cmd=None):
    if cmd:
        success = True
        out = None
        p = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        if p.poll() == 0:
            out, err = p.communicate()
        else:
            success = False
        return success, out

import os
# lsof -i :30301
def start_node():
    abs_path = Path(__file__).parent.absolute()
    target_folder = '%s/../config' % abs_path
    cmd = 'bootnode --genkey=%s/boot.key' % target_folder
    success, _ = run_cmd(cmd)
    print("generate bootnode key:",success)
    if success:
        print("generate bootnode key in:",target_folder)
        cmd = 'bootnode --verbosity 9 --nodekey=%s/boot.key' % target_folder
        p = subprocess.Popen(cmd, shell=True)
        p.wait()

if __name__ == "__main__":
    start_node()
