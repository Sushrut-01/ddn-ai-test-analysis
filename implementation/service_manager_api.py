"""
Service Manager API - Control all services from dashboard
Provides endpoints to start, stop, and check status of all services
Docker-aware: Uses Docker service names when running in container
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
import socket

app = Flask(__name__)
CORS(app)

# Docker environment detection
IS_DOCKER = os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER', 'false').lower() == 'true'

# Docker service name mapping (service_id -> (docker_hostname, internal_port))
# These are the Docker Compose service names that can be resolved within the ddn-network
DOCKER_SERVICE_MAP = {
    "postgresql": ("postgres", 5432),
    "ai_analysis": ("langgraph-service", 5000),
    "dashboard_api": ("dashboard-api", 5006),
    "dashboard_ui": ("dashboard-ui", 5173),
    "n8n": ("n8n", 5678),
    "jenkins": ("jenkins", 8081),
    "reranking": ("reranking-service", 5011),
    "knowledge_api": ("knowledge-management-api", 5015),
    "langfuse": ("langfuse-server", 3000),
    "redis": ("redis", 6379),
    "flower": ("flower", 5555),
    "manual_trigger": ("manual-trigger-api", 5004),
    "jira": ("jira-service", 5009),
    "slack": ("slack-service", 5012),
    "self_healing": ("self-healing-service", 5008),
    "aging": ("aging-service", 5010),
}

print(f"[Service Manager] Running in {'Docker' if IS_DOCKER else 'Local'} mode")

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
        "script": "ai_analysis_service.py",
        "stop_cmd": None,
        "type": "python",
        "process": None
    },
    "dashboard_api": {
        "name": "Dashboard API",
        "port": 5006,
        "script": "start_dashboard_api_port5006.py",
        "stop_cmd": None,
        "type": "python",
        "process": None
    },
    "dashboard_ui": {
        "name": "Dashboard UI",
        "port": 5173,
        "start_cmd": "cd dashboard-ui && npm run dev",
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
        "start_cmd": "cd .. && java -jar jenkins.war --httpPort=8081 --enable-future-java",
        "stop_cmd": None,
        "type": "java",
        "process": None
    },
    "reranking": {
        "name": "Re-Ranking Service",
        "port": 5011,
        "script": "reranking_service.py",
        "stop_cmd": None,
        "type": "python",
        "process": None,
        "description": "Phase 2: CrossEncoder re-ranking for improved RAG accuracy (+15-20%)"
    },
    "knowledge_api": {
        "name": "Knowledge Management API",
        "port": 5015,
        "script": "knowledge_management_api.py",
        "stop_cmd": None,
        "type": "python",
        "process": None,
        "description": "Phase 0-HITL-KM: Human-in-the-loop knowledge management system"
    }
}

def check_port(port, host=None):
    """Check if a port is in use (using socket test - no admin rights needed)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        target_host = host or '127.0.0.1'
        result = sock.connect_ex((target_host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Port check error for {host or '127.0.0.1'}:{port}: {e}")
        return False

def check_service_running(service_id):
    """Check if a service is running, using Docker service names when in Docker"""
    if IS_DOCKER and service_id in DOCKER_SERVICE_MAP:
        docker_host, docker_port = DOCKER_SERVICE_MAP[service_id]
        if docker_port is None:
            return False
        is_running = check_port(docker_port, docker_host)
        print(f"[Docker] Checking {service_id} -> {docker_host}:{docker_port} = {is_running}")
        return is_running
    else:
        if service_id in SERVICES:
            return check_port(SERVICES[service_id]["port"])
        return False

def kill_process_on_port(port):
    """Kill process using a specific port, including parent processes (for Flask watchdog)"""
    killed = False

    try:
        if platform.system() == 'Windows':
            result = subprocess.run(
                f'netstat -ano | findstr ":{port} " | findstr "LISTENING"',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = int(parts[-1])
                        print(f"Found process PID {pid} on port {port}")

                        try:
                            proc = psutil.Process(pid)
                            print(f"Killing process {proc.name()} (PID: {pid})")

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
            "running": check_service_running(service_id)
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

    if check_service_running(service_id):
        print(f"INFO: {service['name']} is already running on port {service['port']}")
        return jsonify({"message": f"{service['name']} is already running"}), 200

    if IS_DOCKER:
        return jsonify({"error": "Cannot start services from within Docker. Use docker-compose to manage services."}), 400

    try:
        print(f"INFO: Starting {service['name']}...")

        if service["type"] == "windows_service":
            print(f"Command: {service['start_cmd']}")
            result = subprocess.run(service["start_cmd"], shell=True, check=True, capture_output=True, text=True)
            print(f"OUTPUT: {result.stdout}")
        elif service["type"] == "python":
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), service["script"])
            print(f"Python: {sys.executable}")
            print(f"Script: {script_path}")

            if platform.system() == 'Windows':
                CREATE_NO_WINDOW = 0x08000000
                CREATE_NEW_PROCESS_GROUP = 0x00000200

                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=os.path.dirname(script_path),
                    creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=os.path.dirname(script_path),
                    start_new_session=True
                )

            service["process"] = process
            print(f"Process started with PID: {process.pid}")
        else:
            print(f"Command: {service.get('start_cmd', 'No start command')}")
            result = subprocess.run(
                service["start_cmd"],
                shell=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=False
            )
            print(f"Start command executed")

        print(f"Waiting 10 seconds for {service['name']} to initialize...")
        time.sleep(10)

        if check_service_running(service_id):
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

    if not check_service_running(service_id):
        print(f"INFO: {service['name']} is not running")
        return jsonify({"message": f"{service['name']} is not running"}), 200

    if IS_DOCKER:
        return jsonify({"error": "Cannot stop services from within Docker. Use docker-compose to manage services."}), 400

    try:
        print(f"INFO: Stopping {service['name']}...")

        if service["type"] == "windows_service":
            print(f"Using Windows service stop command: {service['stop_cmd']}")
            subprocess.run(service["stop_cmd"], shell=True, check=True)
        else:
            print(f"Killing process on port {service['port']}...")
            killed = kill_process_on_port(service["port"])
            if killed:
                print(f"Successfully killed process(es) on port {service['port']}")
            else:
                print(f"WARNING: No processes found to kill on port {service['port']}")

        print("Waiting 2 seconds for service to stop...")
        time.sleep(2)

        if not check_service_running(service_id):
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
    if IS_DOCKER:
        return jsonify({"error": "Cannot start services from within Docker. Use docker-compose to manage services."}), 400

    results = []
    order = ["postgresql", "reranking", "knowledge_api", "ai_analysis", "dashboard_api", "n8n", "jenkins", "dashboard_ui"]

    for service_id in order:
        if service_id in SERVICES:
            try:
                if not check_service_running(service_id):
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
                time.sleep(2)
            except Exception as e:
                results.append({
                    "service": SERVICES[service_id]["name"],
                    "status": f"error: {str(e)}"
                })

    return jsonify({"results": results})

@app.route('/api/services/stop-all', methods=['POST'])
def stop_all():
    """Stop all services in reverse order (excludes Dashboard UI to keep control panel accessible)"""
    if IS_DOCKER:
        return jsonify({"error": "Cannot stop services from within Docker. Use docker-compose to manage services."}), 400

    results = []
    order = ["jenkins", "n8n", "dashboard_api", "ai_analysis", "knowledge_api", "reranking", "postgresql"]

    for service_id in order:
        if service_id in SERVICES:
            try:
                if check_service_running(service_id):
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
    """Restart all services (stop all, then start all)"""
    if IS_DOCKER:
        return jsonify({"error": "Cannot restart services from within Docker. Use docker-compose to manage services."}), 400

    stop_results = stop_all()
    time.sleep(3)
    start_results = start_all()

    return jsonify({
        "message": "All services restarted (Dashboard UI kept running)",
        "results": start_results.json
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Service Manager API",
        "mode": "docker" if IS_DOCKER else "local"
    })

@app.route('/api/services/mode', methods=['GET'])
def get_mode():
    """Get the current running mode (docker or local)"""
    return jsonify({
        "mode": "docker" if IS_DOCKER else "local",
        "docker_services_available": list(DOCKER_SERVICE_MAP.keys()) if IS_DOCKER else []
    })

if __name__ == '__main__':
    print("="*60)
    print("Service Manager API")
    print(f"Mode: {'Docker' if IS_DOCKER else 'Local'}")
    print("="*60)
    print("Control all services from: http://localhost:5007")
    print("="*60)
    app.run(host='0.0.0.0', port=5007, debug=False)
