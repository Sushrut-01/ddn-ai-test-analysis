"""
Updated RAG Architecture Diagram Generator - CORRECTED VERSION
Reflects actual workflow: API scripts store data (not n8n webhooks)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.lines as mlines

# Set up the figure
fig, ax = plt.subplots(1, 1, figsize=(22, 16))
ax.set_xlim(0, 22)
ax.set_ylim(0, 16)
ax.axis('off')

# Color scheme
COLOR_SOURCE = '#E8F4F8'
COLOR_API = '#FFE5F0'
COLOR_DB = '#FFF4E6'
COLOR_AGENT = '#E8F5E9'
COLOR_RAG = '#F3E5F5'
COLOR_MCP = '#FFEBEE'
COLOR_OUTPUT = '#E1F5FE'
COLOR_TRIGGER = '#FFF9C4'
COLOR_ARROW = '#666666'

def add_box(ax, x, y, width, height, text, color, fontsize=10, bold=False):
    """Add a rounded rectangle box with text"""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.1",
        facecolor=color,
        edgecolor='#333333',
        linewidth=2
    )
    ax.add_patch(box)

    weight = 'bold' if bold else 'normal'
    ax.text(
        x + width/2, y + height/2, text,
        ha='center', va='center',
        fontsize=fontsize, weight=weight,
        wrap=True
    )

def add_arrow(ax, x1, y1, x2, y2, label='', style='->'):
    """Add an arrow between two points"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        color=COLOR_ARROW,
        linewidth=2,
        mutation_scale=20
    )
    ax.add_patch(arrow)

    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none'))

# ==================== TITLE ====================
ax.text(11, 15.5, 'DDN AI - RAG ARCHITECTURE (CORRECTED)',
        ha='center', va='center', fontsize=24, weight='bold')
ax.text(11, 15, 'API Scripts Store Data | Manual + Automatic Triggers | RAG Fast Path',
        ha='center', va='center', fontsize=12, style='italic', color='#555555')

# ==================== PHASE 1: BUILD FAILURE & DATA STORAGE ====================
ax.text(3, 14, 'PHASE 1: BUILD FAILURE & DATA STORAGE', ha='center', fontsize=12, weight='bold', color='#C62828')

# Jenkins
add_box(ax, 1, 12.8, 1.8, 0.8, 'Jenkins\nBuild #12345\nFAILS', COLOR_SOURCE, 9, bold=True)

# API Script
add_box(ax, 3.2, 12.8, 2.2, 0.8, 'API Script\n(Python/Shell)\nPost-Build Hook', COLOR_API, 9, bold=True)

# Arrow from Jenkins to API Script
add_arrow(ax, 2.8, 13.2, 3.2, 13.2, 'trigger')

# Databases (Data Storage)
ax.text(8.5, 13.6, 'DATA STORAGE', ha='center', fontsize=10, weight='bold', color='#F57C00')

# PostgreSQL
add_box(ax, 6.5, 12.8, 2, 0.7, 'PostgreSQL', COLOR_DB, 9, bold=True)
ax.text(7.5, 12.55, 'Build metadata, aging_status', ha='center', fontsize=7, color='#666')

# MongoDB
add_box(ax, 8.7, 12.8, 2, 0.7, 'MongoDB', COLOR_DB, 9, bold=True)
ax.text(9.7, 12.55, 'Full logs, GitHub code, test scripts', ha='center', fontsize=7, color='#666')

# Arrows from API Script to Databases
add_arrow(ax, 5.4, 13.2, 6.5, 13.2, 'store')
add_arrow(ax, 5.4, 13.0, 8.7, 13.0, 'store')

# ==================== PHASE 2: TRIGGER MECHANISMS ====================
ax.text(11, 11.8, 'PHASE 2: TRIGGER MECHANISMS', ha='center', fontsize=12, weight='bold', color='#1976D2')

# Automatic Trigger (3-day aging)
add_box(ax, 1, 10.3, 3.5, 1.2, 'Automatic Trigger\n(3-Day Aging)\n\nCron Job checks daily\nDay 3 → aging_status = READY\n→ Calls n8n webhook', COLOR_TRIGGER, 8)

# Manual Trigger (Dashboard)
add_box(ax, 5, 10.3, 3.5, 1.2, 'Manual Trigger\n(Dashboard)\n\nUser clicks "Analyze Now"\nDashboard API → Manual Trigger API\n→ Calls n8n webhook', COLOR_TRIGGER, 8)

# Arrows from databases to triggers
add_arrow(ax, 7.5, 12.8, 2.5, 11.5, '3 days\nlater', '->')
add_arrow(ax, 9.7, 12.8, 6.7, 11.5, 'immediate', '->')

# ==================== n8n ORCHESTRATION ====================
ax.text(11, 9.3, 'n8n ORCHESTRATION LAYER', ha='center', fontsize=12, weight='bold', color='#388E3C')
add_box(ax, 7, 8.5, 8, 0.6, 'Webhook Triggered → Fetch from MongoDB → Call LangGraph Service', COLOR_AGENT, 9)

# Arrows from triggers to n8n
add_arrow(ax, 2.5, 10.3, 9, 9.1, 'webhook')
add_arrow(ax, 6.7, 10.3, 11, 9.1, 'webhook')

# ==================== PINECONE (RIGHT SIDE) ====================
ax.text(19, 13.6, 'VECTOR DATABASE', ha='center', fontsize=10, weight='bold', color='#F57C00')
add_box(ax, 17, 12.8, 4, 0.9, 'Pinecone Vector DB', COLOR_DB, 10, bold=True)
ax.text(19, 12.5, 'Error Embeddings (1536-dim)', ha='center', fontsize=7, color='#666')
ax.text(19, 12.3, 'Historical Solutions', ha='center', fontsize=7, color='#666')

# ==================== LANGGRAPH CLASSIFICATION ====================
ax.text(5, 7.5, 'LANGGRAPH CLASSIFICATION AGENT', ha='center', fontsize=11, weight='bold', color='#7B1FA2')

# Step 1: Fetch from MongoDB
add_box(ax, 2, 6.5, 6, 0.6, 'Step 1: Fetch Complete Context from MongoDB\n(console logs, GitHub code, test scripts, knowledge docs)', COLOR_RAG, 8)

# Step 2: Classification
add_box(ax, 2, 5.7, 6, 0.6, 'Step 2: Error Classification (Keyword Matching → Category)', COLOR_RAG, 8)

# Step 3: Generate Embedding
add_box(ax, 2, 4.9, 6, 0.6, 'Step 3: Generate Embedding (OpenAI → 1536-dim vector)', COLOR_RAG, 8)

# Step 4: Pinecone Search
add_box(ax, 2, 4.1, 6, 0.7, 'Step 4: Pinecone Similarity Search\nTop 5 similar | Filter: error_category', COLOR_RAG, 8)

# Arrow from n8n to LangGraph
add_arrow(ax, 11, 8.5, 5, 6.8, 'call')

# Arrow from LangGraph to Pinecone
add_arrow(ax, 8, 4.5, 17, 13.2, 'search', '<->')

# Arrow from LangGraph to MongoDB (fetch context)
add_arrow(ax, 5, 6.5, 8.7, 13.5, 'fetch\ncontext', '<->')

# ==================== DECISION POINT ====================
decision_x, decision_y = 5, 3
decision_points = [
    (decision_x, decision_y + 0.5),
    (decision_x + 0.8, decision_y),
    (decision_x, decision_y - 0.5),
    (decision_x - 0.8, decision_y)
]
diamond = patches.Polygon(decision_points, closed=True,
                         facecolor='#FFF9C4', edgecolor='#333333', linewidth=2)
ax.add_patch(diamond)
ax.text(decision_x, decision_y, 'RAG or\nMCP?', ha='center', va='center', fontsize=10, weight='bold')

# Arrow from Pinecone search to decision
add_arrow(ax, 5, 4.1, 5, 3.5)

# ==================== RAG PATH (Left - 80%) ====================
ax.text(2, 2, 'RAG FAST PATH (80%)', ha='center', fontsize=11, weight='bold', color='#1976D2')
ax.text(2, 1.75, 'INFRA/CONFIG/DEPEND Errors', ha='center', fontsize=8, style='italic', color='#666')

# RAG solution box
add_box(ax, 0.5, 0.6, 3, 0.9, 'Use RAG Solution\nSimilarity > 0.85\nSuccess Rate > 0.80\nTimes Used > 5\n\nTime: 5s | Cost: $0.01', COLOR_RAG, 8)

# Arrow from decision to RAG
add_arrow(ax, 4.2, 3, 2, 1.5, '80%', '->')

# ==================== MCP PATH (Right - 20%) ====================
ax.text(19, 7, 'MCP DEEP PATH (20%)', ha='center', fontsize=11, weight='bold', color='#C62828')
ax.text(19, 6.75, 'CODE/TEST Errors', ha='center', fontsize=8, style='italic', color='#666')

# MCP Components
add_box(ax, 16, 6, 6, 0.55, 'MongoDB MCP Server (port 5001)\nquery_builds, get_full_logs, get_stack_trace', COLOR_MCP, 7)
add_box(ax, 16, 5.3, 6, 0.55, 'GitHub MCP Server (port 5002)\nfetch_file, search_code, get_commits', COLOR_MCP, 7)
add_box(ax, 16, 4.5, 6, 0.7, 'Claude AI Analysis (claude-3-5-sonnet)\nDeep code analysis + MCP tools → Solution\n\nTime: 15s | Cost: $0.08', COLOR_MCP, 8)

# Arrow from decision to MCP
add_arrow(ax, 5.8, 3, 16, 5.5, '20%', '->')

# Arrows within MCP
add_arrow(ax, 19, 6, 19, 5.85, '', '->')
add_arrow(ax, 19, 5.3, 19, 5.2, '', '->')

# ==================== OUTPUT & STORAGE ====================
ax.text(11, 1.4, 'OUTPUT & NOTIFICATIONS', ha='center', fontsize=11, weight='bold', color='#0277BD')

# Output boxes
add_box(ax, 6, 0.5, 2.2, 0.6, 'Store in MongoDB\nanalysis_solutions', COLOR_OUTPUT, 8)
add_box(ax, 8.4, 0.5, 2.2, 0.6, 'Store in Pinecone\n(for future RAG)', COLOR_OUTPUT, 8)
add_box(ax, 10.8, 0.5, 2.2, 0.6, 'Send Teams\nNotification', COLOR_OUTPUT, 8)
add_box(ax, 13.2, 0.5, 2.2, 0.6, 'Update Dashboard\nwith solution', COLOR_OUTPUT, 8)

# Arrows from paths to output
add_arrow(ax, 2, 0.6, 7, 0.8, '', '->')
add_arrow(ax, 19, 4.5, 11, 1.1, '', '->')

# Arrow from output back to Pinecone (feedback loop)
add_arrow(ax, 9.5, 1.1, 18, 12.8, 'feedback\nloop', '->')

# ==================== KEY INSIGHTS BOX ====================
insights_box_x, insights_box_y = 0.3, 0.05
ax.text(insights_box_x + 5, insights_box_y + 0.2,
        'KEY: API Scripts store data (NOT webhooks) | Manual + Automatic triggers | RAG reduces costs 84% | Gets smarter over time',
        fontsize=9, weight='bold', color='#1565C0',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2))

# ==================== LEGEND ====================
legend_x = 0.3
ax.text(legend_x, 14.8, 'LEGEND:', fontsize=9, weight='bold')
ax.add_patch(patches.Rectangle((legend_x, 14.45), 0.3, 0.15, facecolor=COLOR_SOURCE, edgecolor='#333'))
ax.text(legend_x + 0.4, 14.52, 'Build Source', fontsize=7)

ax.add_patch(patches.Rectangle((legend_x, 14.2), 0.3, 0.15, facecolor=COLOR_API, edgecolor='#333'))
ax.text(legend_x + 0.4, 14.27, 'API Scripts', fontsize=7)

ax.add_patch(patches.Rectangle((legend_x, 13.95), 0.3, 0.15, facecolor=COLOR_DB, edgecolor='#333'))
ax.text(legend_x + 0.4, 14.02, 'Databases', fontsize=7)

ax.add_patch(patches.Rectangle((legend_x, 13.7), 0.3, 0.15, facecolor=COLOR_TRIGGER, edgecolor='#333'))
ax.text(legend_x + 0.4, 13.77, 'Triggers', fontsize=7)

ax.add_patch(patches.Rectangle((legend_x, 13.45), 0.3, 0.15, facecolor=COLOR_AGENT, edgecolor='#333'))
ax.text(legend_x + 0.4, 13.52, 'Orchestration', fontsize=7)

ax.add_patch(patches.Rectangle((legend_x, 13.2), 0.3, 0.15, facecolor=COLOR_RAG, edgecolor='#333'))
ax.text(legend_x + 0.4, 13.27, 'RAG Processing', fontsize=7)

ax.add_patch(patches.Rectangle((legend_x, 12.95), 0.3, 0.15, facecolor=COLOR_MCP, edgecolor='#333'))
ax.text(legend_x + 0.4, 13.02, 'MCP Analysis', fontsize=7)

ax.add_patch(patches.Rectangle((legend_x, 12.7), 0.3, 0.15, facecolor=COLOR_OUTPUT, edgecolor='#333'))
ax.text(legend_x + 0.4, 12.77, 'Output/Storage', fontsize=7)

# Save the diagram
plt.tight_layout()
plt.savefig('RAG-Architecture-Updated.jpg', dpi=300, bbox_inches='tight', facecolor='white')
print("SUCCESS: Updated RAG Architecture Diagram saved as: RAG-Architecture-Updated.jpg")
print("         Resolution: 6600x4800 pixels (300 DPI)")
print("         File format: JPG")
print("         Reflects: API scripts, Manual+Auto triggers, Corrected flow")
