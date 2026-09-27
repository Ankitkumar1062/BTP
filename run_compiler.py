import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    v2_dir = os.path.join(script_dir, "v2_automated_compiler")
    target_script = os.path.join(v2_dir, "run_compiler.py")
    
    cmd = [sys.executable, target_script] + sys.argv[1:]
    res = subprocess.run(cmd, cwd=v2_dir)
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
