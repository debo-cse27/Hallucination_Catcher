import subprocess
import time
import requests

def start_grobid_server():
    print("System: Initializing local extraction service. Please wait...")
    
    # 1. Forcefully clean up any hanging containers from previous manual tests or crashes
    try:
        subprocess.run(["docker", "rm", "-f", "grobid_auto"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    try:
        # 2. Start the container and capture any direct Docker errors
        result = subprocess.run([
            "docker", "run", "-d", "--rm", "--name", "grobid_auto", 
            "-p", "8070:8070", "grobid/grobid:0.8.1"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error: Docker failed to start the container. Details: {result.stderr.strip()}")
            # If port 8070 is still locked by a completely different container, tell the user
            if "port is already allocated" in result.stderr:
                print("System Fix: Please open Docker Desktop, go to 'Containers', and delete any running GROBID containers, then try again.")
            return False
        
        print("System: Container started. Loading AI models into memory (this may take sometime, Thank you for Your Patience!)...")
        
        # 3. Poll the server (Increased timeout to 60 loops * 2 seconds = 120 seconds)
        for _ in range(100):
            try:
                response = requests.get("http://localhost:8070/api/isalive", timeout=2)
                if response.status_code == 200:
                    print("System: Extraction service is active and ready.")
                    return True
            except (requests.ConnectionError, requests.Timeout):
                time.sleep(2)
                
        print("Error: Service initialization timed out. The system took too long to load.")
        return False
        
    except FileNotFoundError:
        print("Error: Docker runtime not found. Please ensure Docker Desktop is installed and running.")
        return False
    except Exception as e:
        print(f"Error: An unexpected issue occurred: {e}")
        return False

def stop_grobid_server():
    print("System: Terminating local extraction service...")
    try:
        # Using rm -f forcefully stops and removes the container to guarantee clean up
        subprocess.run(["docker", "rm", "-f", "grobid_auto"], 
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("System: Service terminated successfully.")
    except Exception:
        print("Warning: Could not automatically terminate the service.")