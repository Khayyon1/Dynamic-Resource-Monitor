import subprocess
import sys
import os

if __name__ == "__main__":
    # Ensure the script runs from the correct directory
    script_dir = os.path.dirname(os.path.abspath(sys.executable))
    script_dir_one_lvl_up = "\\".join(script_dir.split("\\")[:-1])

    script_path = os.path.join(script_dir_one_lvl_up, "st_monitor.py")
    
    if os.path.exists(script_path):
        subprocess.run(["streamlit", "run", script_path])
    else:
        print("Error: st_monitor.py not found!")
