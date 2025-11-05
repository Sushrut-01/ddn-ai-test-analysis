"""
Add Phase 0-HITL tasks to PROGRESS-TRACKER-WITH-0ARCH.csv
Inserts AFTER Phase 0-ARCH, BEFORE Phase 0F
"""

# Phase 0-HITL tasks (15 tasks total - Human-in-the-Loop Feedback System)
phase_0hitl_tasks = [
    # GROUP 1: UI Feedback Components (8 tasks, 22 hours)
    "PHASE 0-HITL,0-HITL.1,Add Accept/Reject/Refine buttons to FailureDetails,dashboard-ui/src/pages/FailureDetails.jsx,Not Started,CRITICAL,2 hours,None,Add 3 buttons: Accept (green) Reject (red) Refine (yellow). Show validation status. Disable after feedback",
    "PHASE 0-HITL,0-HITL.2,Create FeedbackModal.jsx component,dashboard-ui/src/components/FeedbackModal.jsx,Not Started,CRITICAL,3 hours,0-HITL.1,Modal for Reject (reason dropdown + comment) and Refine (suggestion textarea + options). Loading spinner",
    "PHASE 0-HITL,0-HITL.3,Wire feedback buttons to API,dashboard-ui/src/pages/FailureDetails.jsx,Not Started,CRITICAL,2 hours,0-HITL.2,Accept→feedbackAPI.submit(success). Reject→open modal. Refine→open modal. Toast notifications",
    "PHASE 0-HITL,0-HITL.4,Create BeforeAfterComparison.jsx,dashboard-ui/src/components/BeforeAfterComparison.jsx,Not Started,HIGH,4 hours,None,Side-by-side comparison. Highlight differences. Refinement timeline. Collapsible sections",
    "PHASE 0-HITL,0-HITL.5,Integrate BeforeAfterComparison,dashboard-ui/src/pages/FailureDetails.jsx,Not Started,HIGH,2 hours,0-HITL.4,Fetch refinement history. Show comparison if refinements exist. Refinement count badge",
    "PHASE 0-HITL,0-HITL.6,Create FeedbackStatusBadge.jsx,dashboard-ui/src/components/FeedbackStatusBadge.jsx,Not Started,MEDIUM,1 hour,None,Badge: Accepted (green) Rejected (red) Refined (blue) Pending (gray). Tooltip with details",
    "PHASE 0-HITL,0-HITL.7,Add feedback status to Failures list,dashboard-ui/src/pages/Failures.jsx,Not Started,MEDIUM,2 hours,0-HITL.6,Add Status column. Show FeedbackStatusBadge. Filter: All/Accepted/Rejected/Pending/Refined",
    "PHASE 0-HITL,0-HITL.8,Handle refinement completion notifications,dashboard-ui/src/pages/FailureDetails.jsx,Not Started,HIGH,2 hours,0-HITL.3,Show Processing message. Poll/websocket for completion. Notification when done. Auto-refresh. Highlight changes",

    # GROUP 2: Analytics Dashboard (4 tasks, 10 hours)
    "PHASE 0-HITL,0-HITL.9,Create acceptance rate API endpoint,implementation/dashboard_api_full.py,Not Started,HIGH,2 hours,None,GET /api/analytics/acceptance-rate. Query user_feedback. Calculate percentages. Support date range",
    "PHASE 0-HITL,0-HITL.10,Create refinement effectiveness API,implementation/dashboard_api_full.py,Not Started,HIGH,2 hours,None,GET /api/analytics/refinement-stats. Query refinement_history. Join with feedback. Calculate effectiveness",
    "PHASE 0-HITL,0-HITL.11,Add acceptance rate chart to Dashboard,dashboard-ui/src/pages/Dashboard.jsx,Not Started,HIGH,3 hours,0-HITL.9,AI Validation Status card. Pie chart: Accepted/Rejected/Pending. Line chart: rate over time",
    "PHASE 0-HITL,0-HITL.12,Enable and update Analytics.jsx,dashboard-ui/src/pages/Analytics.jsx,Not Started,MEDIUM,3 hours,0-HITL.9 0-HITL.10,Enable queries. Add Feedback Analytics section. Add Model Performance section. Use recharts",

    # GROUP 3: Database & Backend Enhancements (3 tasks, 8 hours)
    "PHASE 0-HITL,0-HITL.13,Create acceptance_tracking table,implementation/postgresql_schema.sql,Not Started,MEDIUM,2 hours,None,New table: acceptance_tracking with validation_status refinement_count final_acceptance. Indexes. Migration script",
    "PHASE 0-HITL,0-HITL.14,Add acceptance tracking to feedback API,implementation/manual_trigger_api.py,Not Started,HIGH,3 hours,0-HITL.13,Update POST /api/feedback. Insert into acceptance_tracking. Increment refinement_count. Set final_acceptance",
    "PHASE 0-HITL,0-HITL.15,Add feedback status to failures list API,implementation/dashboard_api_full.py,Not Started,HIGH,3 hours,0-HITL.13,Update GET /api/failures. Join with acceptance_tracking. Include validation_status. Add status filter",
]

# Read current file
with open('PROGRESS-TRACKER-WITH-0ARCH.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where to insert (AFTER Phase 0-ARCH, BEFORE Phase 0F)
insert_index = None
for i, line in enumerate(lines):
    if line.startswith('PHASE 0F,0F.1'):
        insert_index = i
        break

if insert_index is None:
    print("ERROR: Could not find insertion point (PHASE 0F,0F.1)")
    exit(1)

# Insert Phase 0-HITL tasks
new_lines = lines[:insert_index] + [task + '\n' for task in phase_0hitl_tasks] + lines[insert_index:]

# Write to new file
with open('PROGRESS-TRACKER-FINAL.csv', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Successfully added {len(phase_0hitl_tasks)} Phase 0-HITL tasks!")
print(f"   Inserted at line {insert_index}")
print(f"   New file created: PROGRESS-TRACKER-FINAL.csv")
print(f"\nAction required: Rename PROGRESS-TRACKER-FINAL.csv to PROGRESS-TRACKER.csv")

print("\nPhase 0-HITL task groups:")
print("  GROUP 1: UI Feedback Components (0-HITL.1 - 0-HITL.8) - 8 tasks, 22 hours")
print("  GROUP 2: Analytics Dashboard (0-HITL.9 - 0-HITL.12) - 4 tasks, 10 hours")
print("  GROUP 3: Database & Backend (0-HITL.13 - 0-HITL.15) - 3 tasks, 8 hours")
print("  TOTAL: 15 tasks, 40 hours (~2 weeks)")
print("\nThis phase comes AFTER Phase 0-ARCH, BEFORE Phase 0F")
print("\nImplementation order:")
print("  1. Phase 0-ARCH (Agentic RAG + CRAG + Fusion RAG) - 3-4 weeks")
print("  2. Phase 0-HITL (Human-in-the-Loop Feedback) - 2 weeks")
print("  3. Phase 0F (System Integration: workflows, triggers, aging) - 1 week")
