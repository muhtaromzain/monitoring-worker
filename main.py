# from wd import WD
import threading
import subprocess

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    api_thread        = threading.Thread(target=run_script, args=("api.py",))
    monitoring_thread = threading.Thread(target=run_script, args=("monitoring.py",))

    api_thread.start()
    monitoring_thread.start()

    api_thread.join()
    monitoring_thread.join()
