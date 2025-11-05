"""
System Status Checker
=====================

Quick script to check status of all components

Usage:
    python check_system_status.py
"""

import requests
import json
from datetime import datetime
from colorama import init, Fore, Style
import sys

# Initialize colorama for Windows
init()

def print_header(text):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{text}")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")

def print_status(component, status, details=None):
    """Print component status with color"""
    if status in ['healthy', 'connected', 'available', 'active']:
        icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
        status_text = f"{Fore.GREEN}{status}{Style.RESET_ALL}"
    elif status in ['degraded', 'warning']:
        icon = f"{Fore.YELLOW}⚠{Style.RESET_ALL}"
        status_text = f"{Fore.YELLOW}{status}{Style.RESET_ALL}"
    else:
        icon = f"{Fore.RED}✗{Style.RESET_ALL}"
        status_text = f"{Fore.RED}{status}{Style.RESET_ALL}"

    print(f"{icon} {component:30s} {status_text}")

    if details:
        for key, value in details.items():
            print(f"   {Fore.BLUE}├─{Style.RESET_ALL} {key}: {value}")

def check_ai_service():
    """Check AI Analysis Service"""
    print_header("AI Analysis Service (Port 5000)")

    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)

        if response.status_code == 200:
            health = response.json()

            # Overall status
            print_status("AI Service", health.get('status', 'unknown'))

            # Components
            if 'components' in health:
                print(f"\n{Fore.CYAN}Components:{Style.RESET_ALL}")

                # Gemini
                gemini = health['components'].get('gemini', {})
                gemini_status = gemini.get('status', 'unknown')
                print_status("  Gemini AI", gemini_status, {
                    'Model': gemini.get('model_name', 'N/A'),
                    'Initialized': gemini.get('model_initialized', False)
                })

                # OpenAI
                openai = health['components'].get('openai', {})
                openai_status = openai.get('status', 'unknown')
                print_status("  OpenAI Embeddings", openai_status, {
                    'Model': openai.get('embedding_model', 'N/A')
                })

                # Pinecone
                pinecone = health['components'].get('pinecone', {})
                pinecone_status = pinecone.get('status', 'unknown')
                details = {}
                if 'total_vectors' in pinecone:
                    details['Vectors'] = pinecone['total_vectors']
                if 'dimension' in pinecone:
                    details['Dimension'] = pinecone['dimension']
                print_status("  Pinecone", pinecone_status, details if details else None)

                # MongoDB
                mongodb = health['components'].get('mongodb', {})
                mongodb_status = mongodb.get('status', 'unknown')
                details = {}
                if 'total_failures' in mongodb:
                    details['Total Failures'] = mongodb['total_failures']
                print_status("  MongoDB", mongodb_status, details if details else None)

                # PostgreSQL
                postgres = health['components'].get('postgresql', {})
                postgres_status = postgres.get('status', 'unknown')
                details = {}
                if 'total_analyses' in postgres:
                    details['Total Analyses'] = postgres['total_analyses']
                print_status("  PostgreSQL", postgres_status, details if details else None)

            # RAG
            print(f"\n{Fore.CYAN}Features:{Style.RESET_ALL}")
            rag_enabled = health.get('rag_enabled', False)
            print_status("  RAG (Error Docs)", 'enabled' if rag_enabled else 'disabled')

        else:
            print_status("AI Service", "error", {"HTTP Status": response.status_code})

    except requests.exceptions.ConnectionError:
        print_status("AI Service", "not running", {"Error": "Connection refused"})
        print(f"{Fore.YELLOW}   Start with: python ai_analysis_service.py{Style.RESET_ALL}")
    except Exception as e:
        print_status("AI Service", "error", {"Error": str(e)[:100]})

def check_dashboard_api():
    """Check Dashboard API"""
    print_header("Dashboard API (Port 5005)")

    try:
        # Check health
        response = requests.get('http://localhost:5005/api/health', timeout=5)

        if response.status_code == 200:
            print_status("Dashboard API", "healthy")

            # Get system status
            try:
                sys_response = requests.get('http://localhost:5005/api/system/status', timeout=5)
                if sys_response.status_code == 200:
                    sys_status = sys_response.json()

                    print(f"\n{Fore.CYAN}Components:{Style.RESET_ALL}")

                    components = sys_status.get('components', {})
                    for name, comp in components.items():
                        status = comp.get('status', 'unknown')
                        details = {}
                        if 'total_failures' in comp:
                            details['Failures'] = comp['total_failures']
                        if 'total_analyses' in comp:
                            details['Analyses'] = comp['total_analyses']
                        if 'total_vectors' in comp:
                            details['Vectors'] = comp['total_vectors']

                        print_status(f"  {name.upper()}", status, details if details else None)

            except:
                pass

            # Get stats
            try:
                stats_response = requests.get('http://localhost:5005/api/stats', timeout=5)
                if stats_response.status_code == 200:
                    stats = stats_response.json()

                    print(f"\n{Fore.CYAN}Statistics:{Style.RESET_ALL}")
                    print(f"   {Fore.BLUE}├─{Style.RESET_ALL} Total Failures: {stats.get('total_failures', 0)}")
                    print(f"   {Fore.BLUE}├─{Style.RESET_ALL} Failures (24h): {stats.get('failures_last_24h', 0)}")
                    print(f"   {Fore.BLUE}├─{Style.RESET_ALL} AI Analyses: {stats.get('total_analyzed', 0)}")
                    print(f"   {Fore.BLUE}└─{Style.RESET_ALL} Avg Confidence: {stats.get('avg_confidence', 0)}")

            except:
                pass

        else:
            print_status("Dashboard API", "error", {"HTTP Status": response.status_code})

    except requests.exceptions.ConnectionError:
        print_status("Dashboard API", "not running", {"Error": "Connection refused"})
        print(f"{Fore.YELLOW}   Start with: python dashboard_api_full.py{Style.RESET_ALL}")
    except Exception as e:
        print_status("Dashboard API", "error", {"Error": str(e)[:100]})

def check_dashboard_ui():
    """Check Dashboard UI"""
    print_header("Dashboard UI (Port 5173)")

    try:
        response = requests.get('http://localhost:5173', timeout=5)

        if response.status_code == 200:
            print_status("Dashboard UI", "running")
            print(f"   {Fore.BLUE}└─{Style.RESET_ALL} Access: http://localhost:5173")
        else:
            print_status("Dashboard UI", "error", {"HTTP Status": response.status_code})

    except requests.exceptions.ConnectionError:
        print_status("Dashboard UI", "not running", {"Error": "Connection refused"})
        print(f"{Fore.YELLOW}   Start with: cd dashboard && npm run dev{Style.RESET_ALL}")
    except Exception as e:
        print_status("Dashboard UI", "error", {"Error": str(e)[:100]})

def check_jenkins():
    """Check Jenkins"""
    print_header("Jenkins (Port 8081)")

    try:
        response = requests.get('http://localhost:8081', timeout=5, allow_redirects=True)

        if response.status_code == 200 or response.status_code == 403:
            print_status("Jenkins", "running")
            print(f"   {Fore.BLUE}└─{Style.RESET_ALL} Access: http://localhost:8081")
        else:
            print_status("Jenkins", "unknown", {"HTTP Status": response.status_code})

    except requests.exceptions.ConnectionError:
        print_status("Jenkins", "not running", {"Error": "Connection refused"})
    except Exception as e:
        print_status("Jenkins", "error", {"Error": str(e)[:100]})

def show_pipeline_flow():
    """Show pipeline flow"""
    print_header("Pipeline Flow")

    try:
        response = requests.get('http://localhost:5005/api/pipeline/flow', timeout=5)

        if response.status_code == 200:
            flow = response.json()

            for stage in flow.get('stages', []):
                stage_num = stage.get('stage')
                stage_name = stage.get('name')
                stage_status = stage.get('status', 'unknown')

                print_status(f"Stage {stage_num}: {stage_name}", stage_status)

                if 'recent_activity' in stage and stage['recent_activity']:
                    print(f"   {Fore.BLUE}└─{Style.RESET_ALL} Recent: {len(stage['recent_activity'])} activities")
                elif 'total_failures' in stage:
                    print(f"   {Fore.BLUE}├─{Style.RESET_ALL} Total: {stage['total_failures']}")
                    print(f"   {Fore.BLUE}└─{Style.RESET_ALL} Last 24h: {stage.get('last_24h', 0)}")

        else:
            print(f"{Fore.YELLOW}Pipeline flow not available{Style.RESET_ALL}")

    except:
        print(f"{Fore.YELLOW}Dashboard API not running - can't check pipeline{Style.RESET_ALL}")

def show_quick_commands():
    """Show quick commands"""
    print_header("Quick Commands")

    commands = [
        ("Check AI Service", "curl http://localhost:5000/api/health"),
        ("Check Dashboard API", "curl http://localhost:5005/api/health"),
        ("View System Status", "curl http://localhost:5005/api/system/status"),
        ("View Statistics", "curl http://localhost:5005/api/stats"),
        ("View Pipeline Flow", "curl http://localhost:5005/api/pipeline/flow"),
        ("View Recent Activity", "curl http://localhost:5005/api/activity"),
        ("View Test Failures", "curl http://localhost:5005/api/failures"),
    ]

    for desc, cmd in commands:
        print(f"{Fore.CYAN}• {desc}{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}{cmd}{Style.RESET_ALL}")
        print()

def main():
    """Main function"""
    print(f"\n{Fore.GREEN}{'=' * 70}")
    print(f"{Fore.GREEN}DDN AI Test Analysis System - Status Check{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'=' * 70}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")

    # Check all services
    check_ai_service()
    check_dashboard_api()
    check_dashboard_ui()
    check_jenkins()

    # Show pipeline
    show_pipeline_flow()

    # Show commands
    show_quick_commands()

    print(f"\n{Fore.GREEN}{'=' * 70}")
    print(f"Status check complete!")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Status check interrupted{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
