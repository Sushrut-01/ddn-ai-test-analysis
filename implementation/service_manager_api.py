"""
Service Manager API - Control all services from dashboard
Provides endpoints to start, stop, and check status of all services
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import psutil
import os
import signal
import time
import json
import sys
import platform

app = Flask(__name__)
CORS(app)

# Service configurations
SERVICES = {
    "postgresql": {
        "name": "PostgreSQL Database",
        "port": 5432,
        "start_cmd": "net start postgresql-x64-18",
        "stop_cmd": "net stop postgresql-x64-18",
        "type": "windows_service"
    },
    "ai_analysis": {
        "name": "AI Analysis Service",
        "port": 5000,
        "script": "ai_analysis_service.py",  # Python script to run
        "stop_cmd": None,  # Will use port to find and kill
        "type": "python",
        "process": None
    },
    "dashboard_api": {
        "name": "Dashboard API",
        "port": 5006,
        "script": "start_dashboard_api_port5006.py",  # Python script to run
        "stop_cmd": None,
        "type": "python",
        "process": None
    },
    "dashboard_ui": {
        "name": "Dashboard UI",
        "port": 5173,
        "start_cmd": "cd dashboard-ui && npm run dev",  # Relative to implementation/ directory
        "stop_cmd": None,
        "type": "node",
        "process": None
    },
    "n8n": {
        "name": "n8n Workflows",
        "port": 5678,
        "start_cmd": "n8n start",
        "stop_cmd": None,
        "type": "node",
        "process": None
    },
    "jenkins": {
        "name": "Jenkins CI/CD",
        "port": 8081,
        "start_cmd": "cd .. && java -jar jenkins.war --httpPort=8081 --enable-future-java",  # Go up one level to find jenkins.war
        "stop_cmd": None,
        "type": "java",
        "process": None
    },
    "reranking": {
        "name": "Re-Ranking Service",
        "port": 5009,
        "script": "reranking_service.py",  # Python script to run
        "stop_cmd": None,  # Will use port to find and kill
        "type": "python",
        "process": None,
        "description": "Phase 2: CrossEncoder re-ranking for improved RAG accuracy (+15-20%)"
    },
    "knowledge_api": {
        "name": "Knowledge Management API",
        "port": 5008,
        "script": "knowledge_management_api.py",  # Python script to run
        "stop_cmd": None,  # Will use port to find and kill
        "type": "python",
        "process": None,
        "description": "Phase 0-HITL-KM: Human-in-the-loop knowledge management system"
    }
}

def check_port(port):
    """Check if a port is in use (using socket test - no admin rights needed)"""
    import socket
    try:
        # Try to connect to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 second timeout
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        # If connect_ex returns 0, the port is listening
        return result == 0
    except Exception as e:
        print(f"Port check error for {port}: {e}")
        return False

def kill_process_on_port(port):
    """Kill process using a specific port, including parent processes (for Flask watchdog)"""
    killed = False

    try:
        # Use netstat to find PID (works without admin rights on Windows)
        import platform
        if platform.system() == 'Windows':
            # Use netstat to find PID on Windows
            result = subprocess.run(
                f'netstat -ano | findstr ":{port} " | findstr "LISTENING"',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout:
                # Parse netstat output to get PID
                # Example line: "  TCP    0.0.0.0:5000           0.0.0.0:0              LISTENING       12345"
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = int(parts[-1])
                        print(f"Found process PID {pid} on port {port}")

                        try:
                            proc = psutil.Process(pid)
                            print(f"Killing process {proc.name()} (PID: {pid})")

                            # Also kill parent if it's a Python/Node/Java process (Flask watchdog)
                            try:
                                parent = proc.parent()
                                if parent and parent.name() in ['python.exe', 'python', 'node.exe', 'node', 'java.exe', 'java']:
                                    print(f"Also killing parent process {parent.name()} (PID: {parent.pid})")
                                    parent.terminate()
                                    time.sleep(0.5)
                                    if parent.is_running():
                                        parent.kill()
                            except:
                                pass

                            # Kill the main process
                            proc.terminate()
                            time.sleep(0.5)
                            if proc.is_running():
                                proc.kill()
                            killed = True
                            print(f"Successfully killed process on port {port}")
                        except psutil.NoSuchProcess:
                            print(f"Process {pid} no longer exists")
                        except Exception as e:
                            print(f"Error killing process {pid}: {e}")
        else:
            # Unix/Linux: use lsof
            result = subprocess.run(
                f'lsof -ti:{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid_str in pids:
                    try:
                        pid = int(pid_str)
                        proc = psutil.Process(pid)
                        print(f"Killing process {proc.name()} (PID: {pid})")
                        proc.terminate()
                        time.sleep(0.5)
                        if proc.is_running():
                            proc.kill()
                        killed = True
                    except:
                        continue

    except Exception as e:
        print(f"Error in kill_process_on_port: {e}")

    return killed

def get_service_status():
    """Get status of all services"""
    status = {}
    for service_id, service in SERVICES.items():
        status[service_id] = {
            "name": service["name"],
            "port": service["port"],
            "running": check_port(service["port"])
        }
    return status

@app.route('/api/services/status', methods=['GET'])
def status():
    """Get current status of all services"""
    return jsonify(get_service_status())

@app.route('/api/services/start/<service_id>', methods=['POST'])
def start_service(service_id):
    """Start a specific service"""
    print(f"\n{'='*60}")
    print(f"START REQUEST: {service_id}")
    print(f"{'='*60}")

    if service_id not in SERVICES:
        print(f"ERROR: Service {service_id} not found")
        return jsonify({"error": "Service not found"}), 404

    service = SERVICES[service_id]

    # Check if already running
    if check_port(service["port"]):
        print(f"INFO: {service['name']} is already running on port {service['port']}")
        return jsonify({"message": f"{service['name']} is already running"}), 200

    try:
        print(f"INFO: Starting {service['name']}...")

        if service["type"] == "windows_service":
            print(f"Command: {service['start_cmd']}")
            result = subprocess.run(service["start_cmd"], shell=True, check=True, capture_output=True, text=True)
            print(f"OUTPUT: {result.stdout}")
        elif service["type"] == "python":
            # Start Python service using sys.executable for proper process creation
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), service["script"])
            print(f"Python: {sys.executable}")
            print(f"Script: {script_path}")

            # Create background process on Windows
            if platform.system() == 'Windows':
                # Use CREATE_NO_WINDOW to run without console window
                CREATE_NO_WINDOW = 0x08000000
                CREATE_NEW_PROCESS_GROUP = 0x00000200

                # Don't use DEVNULL - let process inherit parent's environment
                # This ensures .env file is loaded correctly
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=os.path.dirname(script_path),
                    creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Unix/Linux
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=os.path.dirname(script_path),
                    start_new_session=True
                )

            service["process"] = process
            print(f"Process started with PID: {process.pid}")
        else:
            # Other service types (Node, Java) - use shell command
            print(f"Command: {service.get('start_cmd', 'No start command')}")
            result = subprocess.run(
                service["start_cmd"],
                shell=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=False
            )
            print(f"Start command executed")

        # Wait for service to start (10 seconds to allow for initialization)
        # AI services need time to initialize Gemini, MongoDB, Pinecone, etc.
        print(f"Waiting 10 seconds for {service['name']} to initialize...")
        time.sleep(10)

        # Check if started
        if check_port(service["port"]):
            print(f"SUCCESS: {service['name']} started on port {service['port']}")
            return jsonify({"message": f"{service['name']} started successfully"}), 200
        else:
            print(f"ERROR: {service['name']} did not bind to port {service['port']}")
            return jsonify({"error": f"Failed to start {service['name']} - port {service['port']} not listening"}), 500

    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"{type(e).__name__}: {str(e)}"}), 500

@app.route('/api/services/stop/<service_id>', methods=['POST'])
def stop_service(service_id):
    """Stop a specific service"""
    print(f"\n{'='*60}")
    print(f"STOP REQUEST: {service_id}")
    print(f"{'='*60}")

    if service_id not in SERVICES:
        print(f"ERROR: Service {service_id} not found")
        return jsonify({"error": "Service not found"}), 404

    service = SERVICES[service_id]
    print(f"Service: {service['name']}")
    print(f"Port: {service['port']}")

    # Check if running
    if not check_port(service["port"]):
        print(f"INFO: {service['name']} is not running")
        return jsonify({"message": f"{service['name']} is not running"}), 200

    try:
        print(f"INFO: Stopping {service['name']}...")

        if service["type"] == "windows_service":
            print(f"Using Windows service stop command: {service['stop_cmd']}")
            subprocess.run(service["stop_cmd"], shell=True, check=True)
        else:
            # Kill process on port
            print(f"Killing process on port {service['port']}...")
            killed = kill_process_on_port(service["port"])
            if killed:
                print(f"Successfully killed process(es) on port {service['port']}")
            else:
                print(f"WARNING: No processes found to kill on port {service['port']}")

        # Wait a bit
        print("Waiting 2 seconds for service to stop...")
        time.sleep(2)

        # Check if stopped
        if not check_port(service["port"]):
            print(f"SUCCESS: {service['name']} stopped successfully")
            return jsonify({"message": f"{service['name']} stopped successfully"}), 200
        else:
            print(f"ERROR: {service['name']} still running on port {service['port']}")
            return jsonify({"error": f"Failed to stop {service['name']}"}), 500

    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/services/start-all', methods=['POST'])
def start_all():
    """Start all services in correct order"""
    results = []

    # Start in order: Database first, reranking (for AI), then backend, then frontend
    # Reranking MUST start before ai_analysis so AI service can detect it on startup
    # knowledge_api is independent and can start anytime
    order = ["postgresql", "reranking", "knowledge_api", "ai_analysis", "dashboard_api", "n8n", "jenkins", "dashboard_ui"]

    for service_id in order:
        if service_id in SERVICES:
            try:
                if not check_port(SERVICES[service_id]["port"]):
                    response = start_service(service_id)
                    results.append({
                        "service": SERVICES[service_id]["name"],
                        "status": "started"
                    })
                else:
                    results.append({
                        "service": SERVICES[service_id]["name"],
                        "status": "already running"
                    })
                time.sleep(2)  # Wait between services
            except Exception as e:
                results.append({
                    "service": SERVICES[service_id]["name"],
                    "status": f"error: {str(e)}"
                })

    return jsonify({"results": results})

@app.route('/api/services/stop-all', methods=['POST'])
def stop_all():
    """Stop all services in reverse order (excludes Dashboard UI to keep control panel accessible)"""
    results = []

    # Stop in reverse order: Backend services, then database
    # NOTE: Dashboard UI is EXCLUDED to keep the control panel accessible
    order = ["jenkins", "n8n", "dashboard_api", "ai_analysis", "knowledge_api", "reranking", "postgresql"]

    for service_id in order:
        if service_id in SERVICES:
            try:
                if check_port(SERVICES[service_id]["port"]):
                    response = stop_service(service_id)
                    results.append({
                        "service": SERVICES[service_id]["name"],
                        "status": "stopped"
                    })
                else:
                    results.append({
                        "service": SERVICES[service_id]["name"],
                        "status": "not running"
                    })
            except Exception as e:
                results.append({
                    "service": SERVICES[service_id]["name"],
                    "status": f"error: {str(e)}"
                })

    return jsonify({"results": results})

@app.route('/api/services/restart-all', methods=['POST'])
def restart_all():
    """Restart all services (stop all, then start all)
    NOTE: Dashboard UI remains running to keep control panel accessible"""
    # First stop all (excludes dashboard_ui)
    stop_results = stop_all()
    time.sleep(3)

    # Then start all
    start_results = start_all()

    return jsonify({
        "message": "All services restarted (Dashboard UI kept running)",
        "results": start_results.json
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Service Manager API"})

if __name__ == '__main__':
    print("="*60)
    print("Service Manager API")
    print("="*60)
    print("Control all services from: http://localhost:5007")
    print("="*60)
    app.run(host='0.0.0.0', port=5007, debug=False)