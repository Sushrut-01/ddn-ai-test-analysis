# GitHub API Proxy endpoints - Add to mcp_github_server.py before health check

GITHUB_PROXY_CODE = '''
@app.route('/repos/<owner>/<repo>/pulls', methods=['GET'])
def get_pull_requests(owner, repo):
    """Proxy endpoint for GitHub PRs API"""
    try:
        state = request.args.get('state', 'open')
        response = requests.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls",
            headers=get_github_headers(),
            params={'state': state, 'per_page': 100},
            timeout=30
        )
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''
