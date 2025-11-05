"""
Append task summary to PROGRESS-TRACKER.csv
"""

# Read the summary
with open('task_summary.txt', 'r', encoding='utf-8') as f:
    summary_content = f.read()

# Append to progress tracker
with open('PROGRESS-TRACKER.csv', 'a', encoding='utf-8') as f:
    f.write(summary_content)

print("Summary appended successfully!")
