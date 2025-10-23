import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

# Create a large figure for clarity
fig, ax = plt.subplots(figsize=(36, 24))
ax.set_xlim(0, 36)
ax.set_ylim(0, 24)
ax.axis('off')

# Title
ax.text(18, 23, 'VECTOR vs NON-VECTOR DATA FLOW',
        fontsize=48, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', edgecolor='navy', linewidth=3))

# Color scheme
COLOR_NONVECTOR = '#E3F2FD'  # Light blue - MongoDB (NO vectors)
COLOR_VECTOR = '#FFE0B2'      # Light orange - Pinecone (vectors)
COLOR_RAG = '#C8E6C9'         # Light green - RAG path
COLOR_MCP = '#FFF9C4'         # Light yellow - MCP path
COLOR_DECISION = '#F8BBD0'    # Light pink - Decision point

# ============================================================================
# PHASE 1: BUILD FAILURE AND DATA COLLECTION (NO VECTORIZATION)
# ============================================================================
y_start = 20

# Build failure box
build_box = FancyBboxPatch((1, y_start), 5, 1.5,
                           boxstyle="round,pad=0.1",
                           facecolor='#FFCDD2', edgecolor='red', linewidth=3)
ax.add_patch(build_box)
ax.text(3.5, y_start+0.75, 'BUILD #12345\nFAILS',
        fontsize=16, weight='bold', ha='center', va='center')

# Arrow to data collection
ax.annotate('', xy=(8, y_start+0.75), xytext=(6, y_start+0.75),
            arrowprops=dict(arrowstyle='->', lw=3, color='red'))

# Data collection box (13.5 MB - NO VECTORIZATION)
data_box = FancyBboxPatch((8, y_start-1), 6, 3.5,
                          boxstyle="round,pad=0.1",
                          facecolor=COLOR_NONVECTOR, edgecolor='blue', linewidth=3)
ax.add_patch(data_box)
ax.text(11, y_start+1.2, 'DATA COLLECTION', fontsize=18, weight='bold', ha='center')
ax.text(11, y_start+0.7, '13.5 MB TOTAL', fontsize=14, weight='bold', ha='center', color='navy')
ax.text(11, y_start+0.2, 'Console Logs: 8.5 MB', fontsize=12, ha='center')
ax.text(11, y_start-0.2, 'XML Reports: 3 MB', fontsize=12, ha='center')
ax.text(11, y_start-0.6, 'Debug Reports: 2 MB', fontsize=12, ha='center')

# NO VECTOR label
ax.text(11, y_start-1.3, 'NO VECTORIZATION',
        fontsize=14, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='red', linewidth=2))

# Arrow to MongoDB
ax.annotate('', xy=(17, y_start+0.75), xytext=(14, y_start+0.75),
            arrowprops=dict(arrowstyle='->', lw=3, color='blue'))
ax.text(15.5, y_start+1.3, 'Store ALL data', fontsize=11, ha='center', style='italic')
ax.text(15.5, y_start+1, 'as-is (NO vectors)', fontsize=11, ha='center', style='italic', color='red')

# MongoDB storage box
mongo_box = FancyBboxPatch((17, y_start-1), 6, 3.5,
                           boxstyle="round,pad=0.1",
                           facecolor=COLOR_NONVECTOR, edgecolor='green', linewidth=3)
ax.add_patch(mongo_box)
ax.text(20, y_start+1.2, 'MongoDB Storage', fontsize=18, weight='bold', ha='center')
ax.text(20, y_start+0.5, 'Build: BUILD_12345', fontsize=11, ha='center', family='monospace')
ax.text(20, y_start+0.1, 'console_log: "8.5 MB..."', fontsize=11, ha='center', family='monospace')
ax.text(20, y_start-0.3, 'xml_reports: {...}', fontsize=11, ha='center', family='monospace')
ax.text(20, y_start-0.7, 'github_files: {...}', fontsize=11, ha='center', family='monospace')

# NO VECTOR label for MongoDB
ax.text(20, y_start-1.3, 'STORED AS DOCUMENTS',
        fontsize=12, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='green', linewidth=2))

# ============================================================================
# PHASE 2: ERROR TEXT EXTRACTION (ONLY THIS GETS VECTORIZED)
# ============================================================================
y_extract = 15

# Arrow down from MongoDB
ax.annotate('', xy=(20, y_extract+2.5), xytext=(20, y_start-1),
            arrowprops=dict(arrowstyle='->', lw=3, color='purple'))
ax.text(21, y_extract+3, 'Extract error', fontsize=11, ha='left', style='italic')

# Error extraction box
extract_box = FancyBboxPatch((17, y_extract), 6, 2.5,
                             boxstyle="round,pad=0.1",
                             facecolor='#FFF3E0', edgecolor='orange', linewidth=3)
ax.add_patch(extract_box)
ax.text(20, y_extract+2, 'ERROR TEXT EXTRACTION', fontsize=16, weight='bold', ha='center')
ax.text(20, y_extract+1.4, 'ONLY Error Text (200 chars)', fontsize=12, ha='center', color='orange', weight='bold')
ax.text(20, y_extract+0.9, '"OutOfMemoryError: Java heap', fontsize=10, ha='center', family='monospace')
ax.text(20, y_extract+0.5, 'space at DDNStorage.java:127"', fontsize=10, ha='center', family='monospace')

# THIS GETS VECTORIZED label
ax.text(20, y_extract+0, 'THIS GETS VECTORIZED',
        fontsize=14, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', edgecolor='orange', linewidth=3))

# ============================================================================
# PHASE 3: VECTORIZATION WITH OPENAI
# ============================================================================
y_vector = 11

# Arrow to OpenAI
ax.annotate('', xy=(20, y_vector+2), xytext=(20, y_extract),
            arrowprops=dict(arrowstyle='->', lw=3, color='orange'))

# OpenAI embedding box
openai_box = FancyBboxPatch((17, y_vector), 6, 2,
                            boxstyle="round,pad=0.1",
                            facecolor=COLOR_VECTOR, edgecolor='darkorange', linewidth=3)
ax.add_patch(openai_box)
ax.text(20, y_vector+1.4, 'OpenAI Embeddings', fontsize=16, weight='bold', ha='center')
ax.text(20, y_vector+0.9, 'text-embedding-3-small', fontsize=12, ha='center', style='italic')
ax.text(20, y_vector+0.4, '200 chars -> [1536 floats]', fontsize=12, ha='center', family='monospace', weight='bold')
ax.text(20, y_vector-0.1, 'Vector: [0.023, -0.041, 0.018...]', fontsize=10, ha='center', family='monospace')

# ============================================================================
# PHASE 4: PINECONE SEARCH
# ============================================================================
y_pinecone = 7

# Arrow to Pinecone
ax.annotate('', xy=(20, y_pinecone+2.5), xytext=(20, y_vector),
            arrowprops=dict(arrowstyle='->', lw=3, color='darkorange'))
ax.text(21, y_pinecone+3, 'Search similar', fontsize=11, ha='left', style='italic')

# Pinecone search box
pinecone_box = FancyBboxPatch((17, y_pinecone), 6, 2.5,
                              boxstyle="round,pad=0.1",
                              facecolor=COLOR_VECTOR, edgecolor='brown', linewidth=3)
ax.add_patch(pinecone_box)
ax.text(20, y_pinecone+2, 'PINECONE SEARCH', fontsize=16, weight='bold', ha='center')
ax.text(20, y_pinecone+1.4, 'Compare vectors using', fontsize=12, ha='center')
ax.text(20, y_pinecone+1, 'Cosine Similarity', fontsize=12, ha='center', weight='bold')
ax.text(20, y_pinecone+0.5, 'Find top 5 matches', fontsize=11, ha='center', style='italic')
ax.text(20, y_pinecone+0, 'Similarity scores: 0.0 - 1.0', fontsize=11, ha='center', family='monospace')

# ============================================================================
# PHASE 5: DECISION POINT (RAG vs MCP)
# ============================================================================
y_decision = 3

# Arrow to decision
ax.annotate('', xy=(20, y_decision+2.2), xytext=(20, y_pinecone),
            arrowprops=dict(arrowstyle='->', lw=3, color='purple'))

# Decision diamond
decision_box = FancyBboxPatch((17.5, y_decision), 5, 2.2,
                              boxstyle="round,pad=0.1",
                              facecolor=COLOR_DECISION, edgecolor='purple', linewidth=4)
ax.add_patch(decision_box)
ax.text(20, y_decision+1.6, 'DECISION LOGIC', fontsize=16, weight='bold', ha='center')
ax.text(20, y_decision+1.1, 'Similarity > 0.85?', fontsize=13, ha='center', weight='bold')
ax.text(20, y_decision+0.7, 'Success Rate > 80%?', fontsize=13, ha='center', weight='bold')
ax.text(20, y_decision+0.3, 'Times Used > 5?', fontsize=13, ha='center', weight='bold')

# ============================================================================
# PATH A: RAG (80% CASES - REUSE VECTOR)
# ============================================================================
rag_x = 8

# Arrow to RAG
ax.annotate('', xy=(rag_x+2.5, y_decision+1.1), xytext=(17.5, y_decision+1.1),
            arrowprops=dict(arrowstyle='->', lw=4, color='green'))
ax.text(13, y_decision+1.5, 'YES', fontsize=14, weight='bold', ha='center', color='green')
ax.text(13, y_decision+0.7, '(80% cases)', fontsize=12, ha='center', color='green')

# RAG box
rag_box = FancyBboxPatch((rag_x, y_decision-0.5), 5, 3,
                         boxstyle="round,pad=0.1",
                         facecolor=COLOR_RAG, edgecolor='green', linewidth=4)
ax.add_patch(rag_box)
ax.text(rag_x+2.5, y_decision+2, 'RAG PATH', fontsize=18, weight='bold', ha='center', color='darkgreen')
ax.text(rag_x+2.5, y_decision+1.5, '5 seconds | $0.01', fontsize=13, ha='center', weight='bold')
ax.text(rag_x+2.5, y_decision+1, 'REUSE Existing Vector', fontsize=13, ha='center', color='green', weight='bold')
ax.text(rag_x+2.5, y_decision+0.5, 'Return stored solution', fontsize=12, ha='center')
ax.text(rag_x+2.5, y_decision+0.1, 'Increment usage_count', fontsize=11, ha='center', style='italic')
ax.text(rag_x+2.5, y_decision-0.3, 'Update success_rate', fontsize=11, ha='center', style='italic')

# NO NEW VECTOR label
ax.text(rag_x+2.5, y_decision-0.8, 'NO NEW VECTOR CREATED',
        fontsize=13, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='green', linewidth=3))

# ============================================================================
# PATH B: MCP (20% CASES - CREATE NEW VECTOR)
# ============================================================================
mcp_x = 26

# Arrow to MCP
ax.annotate('', xy=(mcp_x, y_decision+1.1), xytext=(22.5, y_decision+1.1),
            arrowprops=dict(arrowstyle='->', lw=4, color='orange'))
ax.text(24.5, y_decision+1.5, 'NO', fontsize=14, weight='bold', ha='center', color='red')
ax.text(24.5, y_decision+0.7, '(20% cases)', fontsize=12, ha='center', color='orange')

# MCP box
mcp_box = FancyBboxPatch((mcp_x, y_decision-0.5), 5, 3,
                         boxstyle="round,pad=0.1",
                         facecolor=COLOR_MCP, edgecolor='orange', linewidth=4)
ax.add_patch(mcp_box)
ax.text(mcp_x+2.5, y_decision+2, 'MCP PATH', fontsize=18, weight='bold', ha='center', color='darkorange')
ax.text(mcp_x+2.5, y_decision+1.5, '15 seconds | $0.08', fontsize=13, ha='center', weight='bold')
ax.text(mcp_x+2.5, y_decision+1, 'CREATE New Vector', fontsize=13, ha='center', color='orange', weight='bold')
ax.text(mcp_x+2.5, y_decision+0.5, 'Deep analysis with Claude', fontsize=12, ha='center')
ax.text(mcp_x+2.5, y_decision+0.1, 'Access MongoDB + GitHub', fontsize=11, ha='center', style='italic')
ax.text(mcp_x+2.5, y_decision-0.3, 'Generate new solution', fontsize=11, ha='center', style='italic')

# NEW VECTOR label
ax.text(mcp_x+2.5, y_decision-0.8, 'NEW VECTOR CREATED',
        fontsize=13, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='orange', linewidth=3))

# ============================================================================
# BOTTOM: STORAGE SUMMARY
# ============================================================================
y_bottom = 0.5

# Arrow from RAG to bottom
ax.annotate('', xy=(rag_x+2.5, y_bottom+0.8), xytext=(rag_x+2.5, y_decision-0.5),
            arrowprops=dict(arrowstyle='->', lw=2, color='green'))

# Arrow from MCP to bottom
ax.annotate('', xy=(mcp_x+2.5, y_bottom+0.8), xytext=(mcp_x+2.5, y_decision-0.5),
            arrowprops=dict(arrowstyle='->', lw=2, color='orange'))

# Pinecone final storage
pinecone_final = FancyBboxPatch((14, y_bottom), 8, 0.8,
                                boxstyle="round,pad=0.05",
                                facecolor=COLOR_VECTOR, edgecolor='brown', linewidth=2)
ax.add_patch(pinecone_final)
ax.text(18, y_bottom+0.4, 'PINECONE: Only vectors + small metadata (error text, solution, success rate)',
        fontsize=11, ha='center', weight='bold')

# ============================================================================
# LEGEND
# ============================================================================
legend_x = 1
legend_y = 8

# Legend box
legend_box = FancyBboxPatch((legend_x, legend_y-1), 5, 7,
                            boxstyle="round,pad=0.2",
                            facecolor='white', edgecolor='black', linewidth=2)
ax.add_patch(legend_box)

ax.text(legend_x+2.5, legend_y+5.5, 'LEGEND', fontsize=18, weight='bold', ha='center')

# Non-vector data
nonvec_patch = mpatches.Rectangle((legend_x+0.3, legend_y+4.5), 0.5, 0.5,
                                   facecolor=COLOR_NONVECTOR, edgecolor='blue', linewidth=2)
ax.add_patch(nonvec_patch)
ax.text(legend_x+1.2, legend_y+4.75, 'Non-Vector Data', fontsize=12, ha='left', weight='bold')
ax.text(legend_x+0.5, legend_y+4, '(MongoDB: Logs, Reports)', fontsize=10, ha='left', style='italic')

# Vector data
vec_patch = mpatches.Rectangle((legend_x+0.3, legend_y+3), 0.5, 0.5,
                                facecolor=COLOR_VECTOR, edgecolor='orange', linewidth=2)
ax.add_patch(vec_patch)
ax.text(legend_x+1.2, legend_y+3.25, 'Vector Data', fontsize=12, ha='left', weight='bold')
ax.text(legend_x+0.5, legend_y+2.5, '(Pinecone: Embeddings)', fontsize=10, ha='left', style='italic')

# RAG path
rag_patch = mpatches.Rectangle((legend_x+0.3, legend_y+1.5), 0.5, 0.5,
                                facecolor=COLOR_RAG, edgecolor='green', linewidth=2)
ax.add_patch(rag_patch)
ax.text(legend_x+1.2, legend_y+1.75, 'RAG: Reuse Vector', fontsize=12, ha='left', weight='bold', color='green')
ax.text(legend_x+0.5, legend_y+1, '(80% cases, NO new vector)', fontsize=10, ha='left', style='italic')

# MCP path
mcp_patch = mpatches.Rectangle((legend_x+0.3, legend_y+0), 0.5, 0.5,
                                facecolor=COLOR_MCP, edgecolor='orange', linewidth=2)
ax.add_patch(mcp_patch)
ax.text(legend_x+1.2, legend_y+0.25, 'MCP: Create Vector', fontsize=12, ha='left', weight='bold', color='orange')
ax.text(legend_x+0.5, legend_y-0.5, '(20% cases, NEW vector)', fontsize=10, ha='left', style='italic')

# ============================================================================
# KEY INSIGHTS BOX
# ============================================================================
insights_x = 26
insights_y = 15

insights_box = FancyBboxPatch((insights_x, insights_y), 9, 5.5,
                              boxstyle="round,pad=0.3",
                              facecolor='#FFFDE7', edgecolor='black', linewidth=3)
ax.add_patch(insights_box)

ax.text(insights_x+4.5, insights_y+5, 'KEY INSIGHTS', fontsize=18, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', edgecolor='black', linewidth=2))

ax.text(insights_x+0.5, insights_y+4.2, '1. Only 200 chars of error text becomes', fontsize=12, ha='left')
ax.text(insights_x+0.8, insights_y+3.8, 'a vector (NOT 13.5 MB of logs)', fontsize=12, ha='left', weight='bold', color='red')

ax.text(insights_x+0.5, insights_y+3.2, '2. MongoDB stores ALL data as regular', fontsize=12, ha='left')
ax.text(insights_x+0.8, insights_y+2.8, 'documents (NO vectorization)', fontsize=12, ha='left', weight='bold', color='blue')

ax.text(insights_x+0.5, insights_y+2.2, '3. RAG reuses existing vectors (80%),', fontsize=12, ha='left')
ax.text(insights_x+0.8, insights_y+1.8, 'just updates usage count', fontsize=12, ha='left', weight='bold', color='green')

ax.text(insights_x+0.5, insights_y+1.2, '4. MCP creates NEW vectors (20%)', fontsize=12, ha='left')
ax.text(insights_x+0.8, insights_y+0.8, 'for novel error patterns', fontsize=12, ha='left', weight='bold', color='orange')

ax.text(insights_x+0.5, insights_y+0.2, '5. Vectors are just math (1536 floats),', fontsize=12, ha='left')
ax.text(insights_x+0.8, insights_y-0.2, 'used for similarity search only', fontsize=12, ha='left', style='italic')

# ============================================================================
# EXAMPLE DATA SIZE
# ============================================================================
size_x = 26
size_y = 11.5

size_box = FancyBboxPatch((size_x, size_y), 9, 3,
                          boxstyle="round,pad=0.3",
                          facecolor='#E8F5E9', edgecolor='darkgreen', linewidth=3)
ax.add_patch(size_box)

ax.text(size_x+4.5, size_y+2.5, 'DATA SIZE COMPARISON', fontsize=16, weight='bold', ha='center')

ax.text(size_x+0.5, size_y+1.8, 'MongoDB (per build):', fontsize=13, ha='left', weight='bold')
ax.text(size_x+0.8, size_y+1.4, 'Console logs: 8.5 MB', fontsize=12, ha='left')
ax.text(size_x+0.8, size_y+1, 'XML + Debug: 5 MB', fontsize=12, ha='left')
ax.text(size_x+0.8, size_y+0.6, 'Total: 13.5 MB (NO vectors)', fontsize=12, ha='left', color='blue', weight='bold')

ax.text(size_x+0.5, size_y+0.1, 'Pinecone (per error):', fontsize=13, ha='left', weight='bold')
ax.text(size_x+0.8, size_y-0.3, 'Vector: 6 KB (1536 floats * 4 bytes)', fontsize=12, ha='left', color='orange', weight='bold')

plt.tight_layout()
plt.savefig('VECTOR-VS-NONVECTOR-DIAGRAM.jpg', dpi=300, bbox_inches='tight', format='jpg')
print("Diagram created: VECTOR-VS-NONVECTOR-DIAGRAM.jpg")
print("Size: 36x24 inches at 300 DPI for maximum clarity")
print("Shows: Vector vs Non-Vector data flow, RAG vs MCP decision logic")
