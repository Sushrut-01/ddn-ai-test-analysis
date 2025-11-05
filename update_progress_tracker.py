"""
Create updated PROGRESS-TRACKER.csv with summary appended
"""

# Read current progress tracker
with open('PROGRESS-TRACKER.csv', 'r', encoding='utf-8') as f:
    current_content = f.read()

# Read the summary
with open('task_summary.txt', 'r', encoding='utf-8') as f:
    summary_content = f.read()

# Combine and write to new file
with open('PROGRESS-TRACKER-UPDATED.csv', 'w', encoding='utf-8') as f:
    f.write(current_content)
    f.write(summary_content)

print("Updated progress tracker created as PROGRESS-TRACKER-UPDATED.csv")
print("Please close PROGRESS-TRACKER.csv if open, then rename the new file.")
