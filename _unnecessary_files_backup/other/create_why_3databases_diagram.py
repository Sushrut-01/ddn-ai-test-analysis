import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

# Create figure
fig, ax = plt.subplots(figsize=(32, 20))
ax.set_xlim(0, 32)
ax.set_ylim(0, 20)
ax.axis('off')

# Title
ax.text(16, 19, 'WHY YOU NEED ALL 3 DATABASES',
        fontsize=44, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', edgecolor='navy', linewidth=3))

ax.text(16, 18.3, '(Pinecone CANNOT Replace MongoDB + PostgreSQL)',
        fontsize=20, ha='center', style='italic', color='red')

# Colors
COLOR_JENKINS = '#FFCDD2'
COLOR_POSTGRES = '#C5E1A5'
COLOR_MONGO = '#FFE082'
COLOR_PINECONE = '#B3E5FC'
COLOR_ERROR = '#FFCCBC'
COLOR_SUCCESS = '#C8E6C9'

# ============================================================================
# SECTION 1: WHAT EACH DATABASE STORES
# ============================================================================
y_db = 14

# PostgreSQL
postgres_box = FancyBboxPatch((1, y_db), 9, 3.5,
                              boxstyle="round,pad=0.2",
                              facecolor=COLOR_POSTGRES, edgecolor='darkgreen', linewidth=3)
ax.add_patch(postgres_box)
ax.text(5.5, y_db+3, 'PostgreSQL', fontsize=20, weight='bold', ha='center')
ax.text(5.5, y_db+2.5, 'METADATA & FAST QUERIES', fontsize=14, weight='bold', ha='center', color='darkgreen')
ax.text(5.5, y_db+2, 'Stores (per build):', fontsize=12, ha='center', style='italic')
ax.text(5.5, y_db+1.6, 'build_id, status, timestamp', fontsize=11, ha='center', family='monospace')
ax.text(5.5, y_db+1.3, 'duration, test_suite, job_name', fontsize=11, ha='center', family='monospace')
ax.text(5.5, y_db+1, 'Size: ~1 KB', fontsize=11, ha='center', weight='bold', color='green')
ax.text(5.5, y_db+0.6, 'Why Needed:', fontsize=11, ha='center', weight='bold')
ax.text(5.5, y_db+0.3, 'Fast filters, COUNT, GROUP BY, JOINs', fontsize=10, ha='center')
ax.text(5.5, y_db+0, 'Dashboard queries < 0.01s', fontsize=10, ha='center', color='green')

# MongoDB
mongo_box = FancyBboxPatch((11.5, y_db), 9, 3.5,
                           boxstyle="round,pad=0.2",
                           facecolor=COLOR_MONGO, edgecolor='darkorange', linewidth=3)
ax.add_patch(mongo_box)
ax.text(16, y_db+3, 'MongoDB', fontsize=20, weight='bold', ha='center')
ax.text(16, y_db+2.5, 'FULL DATA STORAGE', fontsize=14, weight='bold', ha='center', color='darkorange')
ax.text(16, y_db+2, 'Stores (per build):', fontsize=12, ha='center', style='italic')
ax.text(16, y_db+1.6, 'console_log: 8.5 MB', fontsize=11, ha='center', family='monospace')
ax.text(16, y_db+1.3, 'xml_reports: 3 MB', fontsize=11, ha='center', family='monospace')
ax.text(16, y_db+1, 'Size: ~13.5 MB (ORIGINAL DATA)', fontsize=11, ha='center', weight='bold', color='orange')
ax.text(16, y_db+0.6, 'Why Needed:', fontsize=11, ha='center', weight='bold')
ax.text(16, y_db+0.3, 'Display actual logs to users', fontsize=10, ha='center')
ax.text(16, y_db+0, 'Store binary files, no size limit', fontsize=10, ha='center', color='green')

# Pinecone
pinecone_box = FancyBboxPatch((22, y_db), 9, 3.5,
                              boxstyle="round,pad=0.2",
                              facecolor=COLOR_PINECONE, edgecolor='blue', linewidth=3)
ax.add_patch(pinecone_box)
ax.text(26.5, y_db+3, 'Pinecone', fontsize=20, weight='bold', ha='center')
ax.text(26.5, y_db+2.5, 'SEMANTIC SEARCH', fontsize=14, weight='bold', ha='center', color='blue')
ax.text(26.5, y_db+2, 'Stores (per build):', fontsize=12, ha='center', style='italic')
ax.text(26.5, y_db+1.6, 'Vector: [0.023, -0.041, ...] (1536 floats)', fontsize=11, ha='center', family='monospace')
ax.text(26.5, y_db+1.3, 'Metadata: < 40 KB only', fontsize=11, ha='center', family='monospace', color='red')
ax.text(26.5, y_db+1, 'Size: ~6 KB (JUST MATH)', fontsize=11, ha='center', weight='bold', color='blue')
ax.text(26.5, y_db+0.6, 'Why Needed:', fontsize=11, ha='center', weight='bold')
ax.text(26.5, y_db+0.3, 'Find similar error patterns', fontsize=10, ha='center')
ax.text(26.5, y_db+0, 'Semantic search < 0.5s', fontsize=10, ha='center', color='green')

# ============================================================================
# SECTION 2: THE CRITICAL PROBLEM - VECTOR ONLY
# ============================================================================
y_problem = 9

# Problem box
problem_box = FancyBboxPatch((1, y_problem), 30, 4,
                             boxstyle="round,pad=0.3",
                             facecolor='#FFEBEE', edgecolor='red', linewidth=4)
ax.add_patch(problem_box)

ax.text(16, y_problem+3.5, 'THE CRITICAL PROBLEM WITH VECTOR-ONLY STORAGE',
        fontsize=18, weight='bold', ha='center', color='red')

# Problem 1
ax.text(2, y_problem+2.8, 'PROBLEM 1: Vectors Are Not Human-Readable',
        fontsize=14, weight='bold', ha='left', color='darkred')
ax.text(2.5, y_problem+2.4, 'Original Console Log:', fontsize=11, ha='left', weight='bold')
ax.text(3, y_problem+2.1, '"ERROR: OutOfMemoryError: Java heap space at line 127"', fontsize=10, ha='left', family='monospace', color='green')
ax.text(2.5, y_problem+1.7, 'After Converting to Vector:', fontsize=11, ha='left', weight='bold')
ax.text(3, y_problem+1.4, '[0.023, -0.041, 0.018, -0.067, 0.089, 0.034, ...]', fontsize=10, ha='left', family='monospace', color='red')
ax.text(3, y_problem+1.1, 'User cannot read this! Original text is LOST FOREVER.', fontsize=10, ha='left', style='italic', color='red', weight='bold')

# Problem 2
ax.text(2, y_problem+0.6, 'PROBLEM 2: Pinecone Metadata Limit = 40 KB (Your Data = 13.5 MB)',
        fontsize=14, weight='bold', ha='left', color='darkred')
ax.text(3, y_problem+0.2, '13.5 MB CANNOT FIT into 40 KB limit. Data will be rejected!', fontsize=10, ha='left', style='italic', color='red', weight='bold')

# Problem 3
ax.text(17, y_problem+2.8, 'PROBLEM 3: No SQL Queries',
        fontsize=14, weight='bold', ha='left', color='darkred')
ax.text(17.5, y_problem+2.4, 'PostgreSQL:', fontsize=11, ha='left', weight='bold', color='green')
ax.text(18, y_problem+2.1, 'SELECT COUNT(*) WHERE status=\'FAILURE\'', fontsize=10, ha='left', family='monospace')
ax.text(17.5, y_problem+1.7, 'Pinecone:', fontsize=11, ha='left', weight='bold', color='red')
ax.text(18, y_problem+1.4, 'IMPOSSIBLE - only vector similarity search', fontsize=10, ha='left', family='monospace', color='red')

ax.text(17, y_problem+0.6, 'PROBLEM 4: Cannot Store Binary Files',
        fontsize=14, weight='bold', ha='left', color='darkred')
ax.text(17.5, y_problem+0.2, 'Screenshots, PDFs, heap dumps - Pinecone rejects these!', fontsize=10, ha='left', style='italic', color='red')

# ============================================================================
# SECTION 3: DATA FLOW COMPARISON
# ============================================================================
y_flow = 4

# Left side: WRONG WAY (Vector only)
wrong_box = FancyBboxPatch((1, y_flow-0.5), 14, 4.5,
                           boxstyle="round,pad=0.3",
                           facecolor='#FFEBEE', edgecolor='red', linewidth=3)
ax.add_patch(wrong_box)

ax.text(8, y_flow+3.5, 'WRONG: Vector DB Only',
        fontsize=16, weight='bold', ha='center', color='red')

# Jenkins
jenkins_wrong = FancyBboxPatch((4, y_flow+2.3), 8, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor=COLOR_JENKINS, edgecolor='red', linewidth=2)
ax.add_patch(jenkins_wrong)
ax.text(8, y_flow+2.7, 'Jenkins: 13.5 MB data', fontsize=11, weight='bold', ha='center')

# Arrow down
ax.annotate('', xy=(8, y_flow+1.5), xytext=(8, y_flow+2.3),
            arrowprops=dict(arrowstyle='->', lw=3, color='red'))
ax.text(9, y_flow+1.9, 'Try to store', fontsize=9, ha='left', style='italic')

# Pinecone (wrong)
pinecone_wrong = FancyBboxPatch((4, y_flow+0.5), 8, 0.8,
                                boxstyle="round,pad=0.1",
                                facecolor=COLOR_PINECONE, edgecolor='red', linewidth=3)
ax.add_patch(pinecone_wrong)
ax.text(8, y_flow+0.9, 'Pinecone', fontsize=11, weight='bold', ha='center')

# X mark
ax.text(8, y_flow+0.2, 'X  REJECTED', fontsize=14, weight='bold', ha='center', color='red')
ax.text(8, y_flow-0.1, '40 KB limit exceeded!', fontsize=10, ha='center', color='red', style='italic')

# Right side: CORRECT WAY (All 3 DBs)
correct_box = FancyBboxPatch((17, y_flow-0.5), 14, 4.5,
                             boxstyle="round,pad=0.3",
                             facecolor='#E8F5E9', edgecolor='green', linewidth=3)
ax.add_patch(correct_box)

ax.text(24, y_flow+3.5, 'CORRECT: All 3 Databases',
        fontsize=16, weight='bold', ha='center', color='green')

# Jenkins
jenkins_correct = FancyBboxPatch((20, y_flow+2.3), 8, 0.8,
                                 boxstyle="round,pad=0.1",
                                 facecolor=COLOR_JENKINS, edgecolor='green', linewidth=2)
ax.add_patch(jenkins_correct)
ax.text(24, y_flow+2.7, 'Jenkins: 13.5 MB data', fontsize=11, weight='bold', ha='center')

# API Router
ax.annotate('', xy=(24, y_flow+1.8), xytext=(24, y_flow+2.3),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'))

api_router = FancyBboxPatch((20.5, y_flow+1.3), 7, 0.5,
                            boxstyle="round,pad=0.05",
                            facecolor='yellow', edgecolor='black', linewidth=2)
ax.add_patch(api_router)
ax.text(24, y_flow+1.55, 'API Router: Splits data', fontsize=10, weight='bold', ha='center')

# Arrows to 3 DBs
ax.annotate('', xy=(20, y_flow+0.7), xytext=(22, y_flow+1.3),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'))
ax.annotate('', xy=(24, y_flow+0.7), xytext=(24, y_flow+1.3),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'))
ax.annotate('', xy=(28, y_flow+0.7), xytext=(26, y_flow+1.3),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'))

# 3 Databases
db1 = FancyBboxPatch((18.5, y_flow+0.1), 3, 0.6,
                     boxstyle="round,pad=0.05",
                     facecolor=COLOR_POSTGRES, edgecolor='darkgreen', linewidth=2)
ax.add_patch(db1)
ax.text(20, y_flow+0.4, 'PostgreSQL', fontsize=9, weight='bold', ha='center')
ax.text(20, y_flow+0.15, '1KB meta', fontsize=8, ha='center')

db2 = FancyBboxPatch((22.5, y_flow+0.1), 3, 0.6,
                     boxstyle="round,pad=0.05",
                     facecolor=COLOR_MONGO, edgecolor='darkorange', linewidth=2)
ax.add_patch(db2)
ax.text(24, y_flow+0.4, 'MongoDB', fontsize=9, weight='bold', ha='center')
ax.text(24, y_flow+0.15, '13.5MB full', fontsize=8, ha='center')

db3 = FancyBboxPatch((26.5, y_flow+0.1), 3, 0.6,
                     boxstyle="round,pad=0.05",
                     facecolor=COLOR_PINECONE, edgecolor='blue', linewidth=2)
ax.add_patch(db3)
ax.text(28, y_flow+0.4, 'Pinecone', fontsize=9, weight='bold', ha='center')
ax.text(28, y_flow+0.15, '6KB vector', fontsize=8, ha='center')

# Checkmark
ax.text(24, y_flow-0.2, 'ALL SUCCEED', fontsize=11, weight='bold', ha='center', color='green')

# ============================================================================
# SECTION 4: WHAT HAPPENS WHEN USER REQUESTS DATA
# ============================================================================
y_user = 0.5

user_box = FancyBboxPatch((1, y_user), 30, 3,
                          boxstyle="round,pad=0.3",
                          facecolor='#FFF9C4', edgecolor='black', linewidth=3)
ax.add_patch(user_box)

ax.text(16, y_user+2.6, 'WHAT HAPPENS WHEN USER REQUESTS DATA',
        fontsize=16, weight='bold', ha='center')

# Scenario 1
ax.text(2, y_user+2, 'User: "Show me console log"',
        fontsize=12, weight='bold', ha='left', color='blue')
ax.text(2.5, y_user+1.6, 'Vector-Only Approach:', fontsize=11, ha='left', weight='bold', color='red')
ax.text(3, y_user+1.3, '[0.023, -0.041, ...] <- User sees numbers!', fontsize=10, ha='left', family='monospace', color='red')
ax.text(2.5, y_user+0.9, 'Correct Approach:', fontsize=11, ha='left', weight='bold', color='green')
ax.text(3, y_user+0.6, 'MongoDB returns: "ERROR: OutOfMemory..." <- Readable!', fontsize=10, ha='left', family='monospace', color='green')

# Scenario 2
ax.text(17, y_user+2, 'User: "Count failures last 7 days"',
        fontsize=12, weight='bold', ha='left', color='blue')
ax.text(17.5, y_user+1.6, 'Vector-Only Approach:', fontsize=11, ha='left', weight='bold', color='red')
ax.text(18, y_user+1.3, 'IMPOSSIBLE - no COUNT function', fontsize=10, ha='left', family='monospace', color='red')
ax.text(17.5, y_user+0.9, 'Correct Approach:', fontsize=11, ha='left', weight='bold', color='green')
ax.text(18, y_user+0.6, 'PostgreSQL: SELECT COUNT(*) -> 47 failures', fontsize=10, ha='left', family='monospace', color='green')

# Bottom line
ax.text(16, y_user+0.1, 'CONCLUSION: You MUST use all 3 databases together. Each has unique capabilities.',
        fontsize=13, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', edgecolor='red', linewidth=2))

plt.tight_layout()
plt.savefig('WHY-3-DATABASES-NEEDED.jpg', dpi=300, bbox_inches='tight', format='jpg')
print("Diagram created: WHY-3-DATABASES-NEEDED.jpg")
print("Shows: Why Pinecone cannot replace MongoDB and PostgreSQL")
