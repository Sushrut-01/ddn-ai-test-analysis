"""
Add Phase 0F tasks to PROGRESS-TRACKER-UPDATED.csv
"""

# Phase 0F tasks to insert
phase_0f_tasks = [
    "PHASE 0F,0F.1,Delete deprecated n8n workflows,implementation/workflows/,Not Started,HIGH,30 min,0E.11,Remove 4 old workflows: Production Phase2 Phase3 v2.0.0",
    "PHASE 0F,0F.2,Update auto-trigger workflow for dual-index,implementation/workflows/ddn_ai_complete_workflow.json,Not Started,CRITICAL,2 hours,0F.1 0C.13,Add dual-index RAG queries (knowledge docs + error library). OPTION C routing: CODE_ERROR → Gemini+GitHub",
    "PHASE 0F,0F.3,Update manual trigger workflow for dual-index,implementation/workflows/workflow_2_manual_trigger.json,Not Started,CRITICAL,1.5 hours,0F.2,Same dual-index updates. Preserve manual_trigger flag",
    "PHASE 0F,0F.4,Update refinement workflow for dual-index,implementation/workflows/workflow_3_refinement.json,Not Started,CRITICAL,1.5 hours,0F.3,Same dual-index updates. Preserve refinement history",
    "PHASE 0F,0F.5,Import workflows to n8n,n8n UI import,Not Started,CRITICAL,1 hour,0F.4,Import 3 workflows to n8n. Test each end-to-end. Document workflow IDs",
    "PHASE 0F,0F.6,Create aging_service.py with APScheduler,implementation/aging_service.py,Not Started,CRITICAL,4 hours,0F.5,Cron: Check MongoDB every 6h for failures > 3 days with consecutive_failures >= 3. Auto-trigger n8n. Port 5007",
    "PHASE 0F,0F.7,Create TriggerAnalysis.jsx page,dashboard-ui/src/pages/TriggerAnalysis.jsx,Not Started,HIGH,4 hours,0F.6,New /trigger-analysis page. List unanalyzed failures. Bulk trigger UI. Progress indicator",
    "PHASE 0F,0F.8,Add navigation to TriggerAnalysis page,dashboard-ui/src/components/Layout.jsx,Not Started,MEDIUM,1 hour,0F.7,Add sidebar menu item. Badge with unanalyzed count. Update router",
    "PHASE 0F,0F.9,Add trigger button to FailureDetails.jsx,dashboard-ui/src/pages/FailureDetails.jsx,Not Started,CRITICAL,1 hour,None,Add Analyze with AI button. Wire to triggerAPI.triggerAnalysis(). Show toast notification",
    "PHASE 0F,0F.10,Create GitHub test data repository,https://github.com/Sushrut-01,Not Started,HIGH,1 hour,None,Create repo: ddn-test-data. Add folders: /robot-tests /test-data /test-results /scripts. Copy tests from project",
    "PHASE 0F,0F.11,Update GitHub MCP for new repo,github_client.py + .env,Not Started,HIGH,1 hour,0F.10 0E.3,Update GITHUB_REPO in .env. Test MCP server with new repo. Verify github_get_file works",
]

# Read current file
with open('PROGRESS-TRACKER-UPDATED.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where to insert (after Phase 0E, before Phase 1)
insert_index = None
for i, line in enumerate(lines):
    if line.startswith('PHASE 1,1.1'):
        insert_index = i
        break

if insert_index is None:
    print("ERROR: Could not find insertion point (PHASE 1,1.1)")
    exit(1)

# Insert Phase 0F tasks
new_lines = lines[:insert_index] + [task + '\n' for task in phase_0f_tasks] + lines[insert_index:]

# Write to new file
with open('PROGRESS-TRACKER-WITH-0F.csv', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Successfully added {len(phase_0f_tasks)} Phase 0F tasks!")
print(f"   Inserted at line {insert_index}")
print(f"   New file created: PROGRESS-TRACKER-WITH-0F.csv")
print(f"\nAction required: Rename PROGRESS-TRACKER-WITH-0F.csv to PROGRESS-TRACKER.csv")
print("\nPhase 0F tasks added:")
for i, task in enumerate(phase_0f_tasks, 1):
    task_id = task.split(',')[1]
    task_desc = task.split(',')[2]
    print(f"  {i}. {task_id}: {task_desc}")
