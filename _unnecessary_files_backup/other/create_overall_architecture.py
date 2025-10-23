"""
Overall System Architecture Diagram Generator
High-level view of the complete DDN AI Test Failure Analysis System
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.lines as mlines

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')

# Color scheme
COLOR_SOURCE = '#E8F4F8'
COLOR_API = '#FFE5F0'
COLOR_DB = '#FFF4E6'
COLOR_AI = '#E8F5E9'
COLOR_OUTPUT = '#E1F5FE'
COLOR_HUMAN = '#FFF3E0'

def add_box(ax, x, y, width, height, text, color, fontsize=10, bold=False):
    """Add a rounded rectangle box with text"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.1",
        facecolor=color,
        edgecolor='#333333',
        linewidth=2.5
    )
    ax.add_patch(box)

    weight = 'bold' if bold else 'normal'
    ax.text(
        x + width/2, y + height/2, text,
        ha='center', va='center',
        fontsize=fontsize, weight=weight,
        wrap=True
    )

def add_arrow(ax, x1, y1, x2, y2, label='', style='->', color='#666666', lw=2):
    """Add an arrow between two points"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        color=color,
        linewidth=lw,
        mutation_scale=25
    )
    ax.add_patch(arrow)

    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.3, label, fontsize=9, weight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#333', linewidth=1.5))

# ==================== TITLE ====================
ax.text(10, 13.5, 'DDN AI - COMPLETE SYSTEM ARCHITECTURE',
        ha='center', va='center', fontsize=26, weight='bold')
ax.text(10, 13, 'Automated Test Failure Analysis & Resolution System',
        ha='center', va='center', fontsize=14, style='italic', color='#555555')

# ==================== LAYER 1: DATA SOURCES ====================
ax.text(3, 11.5, 'DATA SOURCES', ha='center', fontsize=12, weight='bold', color='#1976D2')

# GitHub
add_box(ax, 1, 10.2, 1.8, 1, 'GitHub', COLOR_SOURCE, 11, bold=True)
ax.text(1.9, 9.95, 'Source Code\nCommits\nBranches', ha='center', fontsize=7, color='#666')

# Jenkins
add_box(ax, 3.2, 10.2, 1.8, 1, 'Jenkins', COLOR_SOURCE, 11, bold=True)
ax.text(4.1, 9.95, 'CI/CD Builds\nTest Execution\nConsole Logs', ha='center', fontsize=7, color='#666')

# ==================== LAYER 2: API LAYER ====================
ax.text(3, 8.5, 'API SCRIPTS LAYER', ha='center', fontsize=12, weight='bold', color='#C62828')

# API Script Box
add_box(ax, 1.5, 7.3, 3, 0.9, 'Jenkins Post-Build API Scripts\n(Python/Shell)\nData Collection & Storage', COLOR_API, 10, bold=True)

# Arrows from sources to API
add_arrow(ax, 1.9, 10.2, 2.5, 8.2, 'trigger', '->', '#1976D2', 2.5)
add_arrow(ax, 4.1, 10.2, 3.5, 8.2, 'fail event', '->', '#1976D2', 2.5)

# ==================== LAYER 3: DATABASES ====================
ax.text(10, 11.5, 'DATABASE LAYER', ha='center', fontsize=12, weight='bold', color='#F57C00')

# PostgreSQL
add_box(ax, 7, 10.2, 2.5, 1, 'PostgreSQL', COLOR_DB, 11, bold=True)
ax.text(8.25, 9.95, 'Build Metadata\nAging Status\nAnalysis Results', ha='center', fontsize=7, color='#666')

# MongoDB
add_box(ax, 10, 10.2, 2.5, 1, 'MongoDB', COLOR_DB, 11, bold=True)
ax.text(11.25, 9.95, 'Full Logs\nGitHub Code\nTest Scripts\nKnowledge Docs', ha='center', fontsize=7, color='#666')

# Pinecone
add_box(ax, 13, 10.2, 2.5, 1, 'Pinecone', COLOR_DB, 11, bold=True)
ax.text(14.25, 9.95, 'Vector Embeddings\nHistorical Solutions\nSuccess Rates', ha='center', fontsize=7, color='#666')

# Arrows from API to Databases
add_arrow(ax, 3, 7.3, 7.5, 10.2, 'store', '->', '#F57C00', 2.5)
add_arrow(ax, 3.5, 7.3, 11, 10.2, 'store', '->', '#F57C00', 2.5)

# ==================== LAYER 4: TRIGGER LAYER ====================
ax.text(3, 6, 'TRIGGER LAYER', ha='center', fontsize=12, weight='bold', color='#7B1FA2')

# Automatic Trigger
add_box(ax, 1, 5, 2, 0.7, 'Automatic Trigger\n(3-Day Aging Cron)', '#FFF9C4', 9, bold=True)

# Manual Trigger
add_box(ax, 3.5, 5, 2, 0.7, 'Manual Trigger\n(Dashboard API)', '#FFF9C4', 9, bold=True)

# Arrows from databases to triggers
add_arrow(ax, 8, 10.2, 2, 5.7, '3 days', '->', '#7B1FA2', 2)
add_arrow(ax, 11, 10.2, 4.5, 5.7, 'immediate', '->', '#7B1FA2', 2)

# ==================== LAYER 5: AGENTIC AI (THE HEART) ====================
# Large box encompassing the AI system
ai_box = FancyBboxPatch(
    (6.5, 3.5), 9, 3.5,
    boxstyle="round,pad=0.2",
    facecolor=COLOR_AI,
    edgecolor='#2E7D32',
    linewidth=3
)
ax.add_patch(ai_box)

ax.text(11, 6.7, 'AGENTIC AI SYSTEM', ha='center', fontsize=14, weight='bold', color='#2E7D32')

# n8n Orchestration
add_box(ax, 7, 6, 8, 0.5, 'n8n Orchestration - Workflow Automation', '#C8E6C9', 9, bold=True)

# LangGraph + RAG
add_box(ax, 7, 5.1, 3.8, 0.7, 'LangGraph Agent\nClassification + RAG\nPinecone Search', '#A5D6A7', 8, bold=True)

# MCP Servers
add_box(ax, 11.2, 5.1, 3.8, 0.7, 'MCP Servers\nMongoDB MCP | GitHub MCP\nClaude AI Deep Analysis', '#A5D6A7', 8, bold=True)

# Decision arrow
add_arrow(ax, 9, 5.1, 9, 4.8, '', '->', '#2E7D32', 1.5)
add_arrow(ax, 9, 4.8, 8, 4.5, '80% RAG', '->', '#1976D2', 2)
add_arrow(ax, 9, 4.8, 12, 4.5, '20% MCP', '->', '#C62828', 2)

# Results boxes
add_box(ax, 7, 3.8, 3.8, 0.5, 'RAG Path\n5s | $0.01', '#BBDEFB', 8)
add_box(ax, 11.2, 3.8, 3.8, 0.5, 'MCP Path\n15s | $0.08', '#FFCDD2', 8)

# Arrows from triggers to AI
add_arrow(ax, 3, 5.3, 7, 6.2, 'webhook', '->', '#2E7D32', 2.5)
add_arrow(ax, 4.5, 5.3, 10, 6.2, 'webhook', '->', '#2E7D32', 2.5)

# Arrows from AI to databases
add_arrow(ax, 15.5, 5.5, 14, 10.2, 'query', '<->', '#F57C00', 2)
add_arrow(ax, 13, 5.5, 11.5, 10.2, 'query', '<->', '#F57C00', 2)

# ==================== LAYER 6: OUTPUT LAYER ====================
ax.text(10, 2.8, 'OUTPUT & NOTIFICATION LAYER', ha='center', fontsize=12, weight='bold', color='#0277BD')

# Output boxes
add_box(ax, 6.5, 1.5, 2.2, 0.9, 'MongoDB\nStore Solution', COLOR_OUTPUT, 9)
add_box(ax, 9, 1.5, 2.2, 0.9, 'Pinecone\nUpdate Vectors', COLOR_OUTPUT, 9)
add_box(ax, 11.5, 1.5, 2.2, 0.9, 'Teams\nNotification', COLOR_OUTPUT, 9)
add_box(ax, 14, 1.5, 2.2, 0.9, 'Dashboard\nUpdate UI', COLOR_OUTPUT, 9)

# Arrows from AI to outputs
add_arrow(ax, 9, 3.8, 7.5, 2.4, '', '->', '#0277BD', 2.5)
add_arrow(ax, 12, 3.8, 10, 2.4, '', '->', '#0277BD', 2.5)
add_arrow(ax, 12, 3.8, 12.5, 2.4, '', '->', '#0277BD', 2.5)
add_arrow(ax, 12, 3.8, 15, 2.4, '', '->', '#0277BD', 2.5)

# ==================== LAYER 7: HUMAN IN LOOP ====================
ax.text(3, 2.8, 'HUMAN IN THE LOOP', ha='center', fontsize=12, weight='bold', color='#EF6C00')

# Human interaction boxes
add_box(ax, 1, 1.5, 1.8, 0.9, 'Teams\nChannel\nReview', COLOR_HUMAN, 9)
add_box(ax, 3.2, 1.5, 1.8, 0.9, 'Dashboard\nManual Trigger\nFeedback', COLOR_HUMAN, 9)

# Arrows from outputs to human
add_arrow(ax, 11.5, 1.9, 2.8, 1.9, 'notify', '<-', '#EF6C00', 2)
add_arrow(ax, 14, 1.9, 4.1, 1.9, 'display', '<-', '#EF6C00', 2)

# Feedback loop
add_arrow(ax, 4.1, 2.4, 4.5, 5, 'manual\ntrigger', '->', '#7B1FA2', 2.5)
add_arrow(ax, 2, 2.4, 9, 10.2, 'feedback', '->', '#4CAF50', 2)

# ==================== KEY METRICS BOX ====================
metrics_text = (
    "PERFORMANCE METRICS: 84% cost reduction | 61% faster response | "
    "80% handled by RAG (5s, $0.01) | 20% deep analysis (15s, $0.08) | "
    "Learning system: Gets smarter over time"
)
ax.text(10, 0.7, metrics_text,
        ha='center', fontsize=9, weight='bold', color='#1565C0',
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2.5))

# ==================== DATA FLOW LABELS ====================
ax.text(0.5, 12.5, 'DATA FLOW:', fontsize=10, weight='bold')
ax.text(0.5, 12.2, '1. Build fails', fontsize=8)
ax.text(0.5, 11.95, '2. API stores data', fontsize=8)
ax.text(0.5, 11.7, '3. Aging or Manual', fontsize=8)
ax.text(0.5, 11.45, '4. AI Analysis', fontsize=8)
ax.text(0.5, 11.2, '5. Output & Notify', fontsize=8)
ax.text(0.5, 10.95, '6. Human Review', fontsize=8)
ax.text(0.5, 10.7, '7. Feedback Loop', fontsize=8)

# ==================== LEGEND ====================
legend_x = 16.5
ax.text(legend_x, 12.5, 'LEGEND:', fontsize=9, weight='bold')
ax.add_patch(Rectangle((legend_x, 12.15), 0.4, 0.2, facecolor=COLOR_SOURCE, edgecolor='#333', linewidth=1.5))
ax.text(legend_x + 0.5, 12.25, 'Data Sources', fontsize=8)

ax.add_patch(Rectangle((legend_x, 11.85), 0.4, 0.2, facecolor=COLOR_API, edgecolor='#333', linewidth=1.5))
ax.text(legend_x + 0.5, 11.95, 'API Scripts', fontsize=8)

ax.add_patch(Rectangle((legend_x, 11.55), 0.4, 0.2, facecolor=COLOR_DB, edgecolor='#333', linewidth=1.5))
ax.text(legend_x + 0.5, 11.65, 'Databases', fontsize=8)

ax.add_patch(Rectangle((legend_x, 11.25), 0.4, 0.2, facecolor=COLOR_AI, edgecolor='#333', linewidth=1.5))
ax.text(legend_x + 0.5, 11.35, 'AI System', fontsize=8)

ax.add_patch(Rectangle((legend_x, 10.95), 0.4, 0.2, facecolor=COLOR_OUTPUT, edgecolor='#333', linewidth=1.5))
ax.text(legend_x + 0.5, 11.05, 'Outputs', fontsize=8)

ax.add_patch(Rectangle((legend_x, 10.65), 0.4, 0.2, facecolor=COLOR_HUMAN, edgecolor='#333', linewidth=1.5))
ax.text(legend_x + 0.5, 10.75, 'Human Loop', fontsize=8)

# Save the diagram
plt.tight_layout()
plt.savefig('Overall-Architecture.jpg', dpi=300, bbox_inches='tight', facecolor='white')
print("SUCCESS: Overall Architecture Diagram saved as: Overall-Architecture.jpg")
print("         Resolution: 6000x4200 pixels (300 DPI)")
print("         File format: JPG")
print("         Shows: Complete system with all layers and data flow")
