"""
Generate Task Status Summary for PROGRESS-TRACKER.csv
"""
import csv
from collections import defaultdict

# Read the CSV file
tasks_by_phase = defaultdict(lambda: defaultdict(int))

with open('PROGRESS-TRACKER-FINAL.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        phase = row['Phase']
        status = row['Status']

        # Map status to canonical categories
        if 'Completed' in status or 'Complete' in status:
            status_key = 'Completed'
        elif 'In Progress' in status or 'InProgress' in status:
            status_key = 'In Progress'
        elif 'Deferred' in status:
            status_key = 'Deferred'
        elif 'Pending' in status:
            status_key = 'Pending'
        elif 'Not Started' in status:
            status_key = 'Not Started'
        elif 'Not Required' in status:
            status_key = 'Not Required'
        else:
            status_key = 'Other'  # Catch-all for unexpected statuses

        tasks_by_phase[phase][status_key] += 1
        tasks_by_phase[phase]['Total'] += 1

# Calculate overall totals
overall = defaultdict(int)

for phase_data in tasks_by_phase.values():
    for status_key, count in phase_data.items():
        overall[status_key] += count

# Generate summary text
summary_lines = [
    "",
    "# ============================================================================",
    "# TASK STATUS SUMMARY BY PHASE",
    "# ============================================================================",
    "# This summary is auto-generated. Shows task counts by status for each phase.",
    "# Updated: 2025-10-31",
    "# ============================================================================",
    "",
    "Phase,Total Tasks,Completed,In Progress,Not Started,Deferred,Pending,% Complete"
]

# Sort phases for display
phase_order = ['PHASE 0', 'PHASE 0B', 'PHASE 0C', 'PHASE 0D', 'PHASE 0E', 'PHASE 0-ARCH', 'PHASE 0-HITL', 'PHASE 0F'] + \
              [f'PHASE {i}' for i in range(1, 11)] + ['PHASE B']

for phase in phase_order:
    if phase in tasks_by_phase:
        data = tasks_by_phase[phase]
        total = data.get('Total', 0)
        completed = data.get('Completed', 0)
        in_progress = data.get('In Progress', 0)
        not_started = data.get('Not Started', 0)
        deferred = data.get('Deferred', 0)
        pending = data.get('Pending', 0)

        if total > 0:
            pct = (completed / total * 100) if total > 0 else 0
            summary_lines.append(
                f"{phase},{total},{completed},{in_progress},{not_started},{deferred},{pending},{pct:.1f}%"
            )

# Add overall totals
summary_lines.append("")
summary_lines.append("# Overall Project Summary")
total_tasks = overall.get('Total', 0)
completed_tasks = overall.get('Completed', 0)
in_progress_tasks = overall.get('In Progress', 0)
not_started_tasks = overall.get('Not Started', 0)
deferred_tasks = overall.get('Deferred', 0)
pending_tasks = overall.get('Pending', 0)

pct_overall = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
summary_lines.append(
    f"TOTAL,{total_tasks},{completed_tasks},{in_progress_tasks},"
    f"{not_started_tasks},{deferred_tasks},{pending_tasks},{pct_overall:.1f}%"
)

# Print summary
print("\n".join(summary_lines))

# Also save to file
with open('task_summary.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(summary_lines))

print("\n\nSummary saved to task_summary.txt")
