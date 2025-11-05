"""
Add Phase 0-ARCH tasks to PROGRESS-TRACKER-WITH-0F.csv
Inserts BEFORE Phase 0F (proper architecture foundation)
"""

# Phase 0-ARCH tasks (30 tasks total)
phase_0arch_tasks = [
    # GROUP 1: AGENTIC RAG (12 tasks)
    "PHASE 0-ARCH,0-ARCH.1,Research and design ReAct agent architecture,Design docs,Not Started,CRITICAL,4 hours,None,Study gap analysis docs. Design Thought->Action->Observation loops. Map tools to error types",
    "PHASE 0-ARCH,0-ARCH.2,Create react_agent_service.py,implementation/agents/react_agent_service.py,Not Started,CRITICAL,6 hours,0-ARCH.1,ReActAgent class with reasoning loops. ToolExecutor for dynamic selection. Loop termination logic",
    "PHASE 0-ARCH,0-ARCH.3,Implement tool registry,implementation/agents/tool_registry.py,Not Started,CRITICAL,3 hours,0-ARCH.2,Register GitHub MongoDB Pinecone Jenkins tools. Tool selection logic by error category",
    "PHASE 0-ARCH,0-ARCH.4,Implement ReAct reasoning prompts,implementation/agents/thought_prompts.py,Not Started,HIGH,3 hours,0-ARCH.2,Category-specific thought templates. CODE INFRA CONFIG prompts. Few-shot examples",
    "PHASE 0-ARCH,0-ARCH.5,Implement self-correction mechanism,implementation/agents/correction_strategy.py,Not Started,HIGH,2 hours,0-ARCH.2,Retry logic for failed actions. Alternative action selection. Max 3 retries",
    "PHASE 0-ARCH,0-ARCH.6,Update langgraph_agent.py for ReAct,langgraph_agent.py,Not Started,CRITICAL,4 hours,0-ARCH.3,Replace linear workflow with ReAct state graph. Add think/act/observe nodes. Conditional routing",
    "PHASE 0-ARCH,0-ARCH.7,Implement context-aware routing,langgraph_agent.py,Not Started,HIGH,2 hours,0-ARCH.6,80% skip GitHub (INFRA CONFIG DATA). 20% fetch code (CODE_ERROR). Log routing decisions",
    "PHASE 0-ARCH,0-ARCH.8,Add multi-step reasoning,implementation/agents/react_agent_service.py,Not Started,MEDIUM,3 hours,0-ARCH.6,Detect multi-file errors. Plan multi-step retrieval. Reasoning chain storage. Result caching",
    "PHASE 0-ARCH,0-ARCH.9,Create test_react_agent.py,implementation/tests/test_react_agent.py,Not Started,CRITICAL,2 hours,0-ARCH.2,Test thought generation action selection observation self-correction loop termination",
    "PHASE 0-ARCH,0-ARCH.10,Integrate ReAct with ai_analysis_service,ai_analysis_service.py,Not Started,CRITICAL,2 hours,0-ARCH.9,Replace Gemini direct call with ReAct invocation. Pass results to Gemini for formatting",
    "PHASE 0-ARCH,0-ARCH.11,Document ReAct agent architecture,REACT-AGENT-GUIDE.md,Not Started,MEDIUM,1 hour,0-ARCH.10,Document flow. Troubleshooting guide. Example traces",
    "PHASE 0-ARCH,0-ARCH.12,Performance test ReAct agent,Test suite,Not Started,HIGH,2 hours,0-ARCH.10,20 diverse scenarios. Measure iterations latency self-correction. Target: <10s (80%) <30s (20%)",

    # GROUP 2: CRAG (10 tasks)
    "PHASE 0-ARCH,0-ARCH.13,Design CRAG verification layer,Design docs,Not Started,CRITICAL,3 hours,None,Study CRAG docs. Design confidence scoring (0.0-1.0). Define thresholds (high>0.85 medium low)",
    "PHASE 0-ARCH,0-ARCH.14,Create crag_verifier.py,implementation/verification/crag_verifier.py,Not Started,CRITICAL,4 hours,0-ARCH.13,CRAGVerifier class. confidence_score() method. Check relevance consistency grounding",
    "PHASE 0-ARCH,0-ARCH.15,Implement self-correction for low confidence,crag_verifier.py,Not Started,CRITICAL,3 hours,0-ARCH.14,Correction workflow (confidence < 0.85). Query expansion. Retrieve additional context. Re-generate answer",
    "PHASE 0-ARCH,0-ARCH.16,Implement HITL for medium confidence,crag_verifier.py + PostgreSQL,Not Started,HIGH,3 hours,0-ARCH.14,HITL trigger (0.65 < conf < 0.85). hitl_queue table. Teams/Slack notification. Review endpoints",
    "PHASE 0-ARCH,0-ARCH.17,Implement web search fallback,crag_verifier.py,Not Started,MEDIUM,2 hours,0-ARCH.14,Web search trigger (conf < 0.65). Integrate search API. Extract snippets. Re-generate with web results",
    "PHASE 0-ARCH,0-ARCH.18,Integrate CRAG into ai_analysis_service,ai_analysis_service.py,Not Started,CRITICAL,2 hours,0-ARCH.15,Wrap all AI responses with verification. Add confidence to API. Trigger corrections. Log all",
    "PHASE 0-ARCH,0-ARCH.19,Create CRAG evaluation metrics,crag_verifier.py,Not Started,HIGH,2 hours,0-ARCH.18,Track confidence distribution. Self-correction rate. HITL queue size. Accuracy before/after",
    "PHASE 0-ARCH,0-ARCH.20,Create test_crag_verifier.py,implementation/tests/test_crag_verifier.py,Not Started,CRITICAL,2 hours,0-ARCH.14,Test high (pass through) medium (HITL) low (correct) very-low (web search) confidence",
    "PHASE 0-ARCH,0-ARCH.21,Document CRAG verification layer,CRAG-VERIFICATION-GUIDE.md,Not Started,MEDIUM,1 hour,0-ARCH.18,Explain scoring methodology. Self-correction workflow. HITL process",
    "PHASE 0-ARCH,0-ARCH.22,Performance test CRAG layer,Test suite,Not Started,CRITICAL,2 hours,0-ARCH.18,50 diverse errors. Measure false positive/negative. Target: >95% accuracy after CRAG",

    # GROUP 3: FUSION RAG (8 tasks)
    "PHASE 0-ARCH,0-ARCH.23,Design Fusion RAG architecture,Design docs,Not Started,CRITICAL,2 hours,None,Consolidate Phase 2/3/5. Design multi-source RRF. Plan 4 sources: Pinecone BM25 MongoDB PostgreSQL",
    "PHASE 0-ARCH,0-ARCH.24,Create fusion_rag_service.py,implementation/retrieval/fusion_rag_service.py,Not Started,CRITICAL,4 hours,0-ARCH.23,FusionRAG class. Parallel retrieval from 4 sources. Dense sparse full-text structured search",
    "PHASE 0-ARCH,0-ARCH.25,Implement BM25 index builder,implementation/retrieval/build_bm25_index.py,Not Started,CRITICAL,2 hours,0-ARCH.24,Index MongoDB errors. Index Pinecone metadata. Store BM25 index. Incremental updates",
    "PHASE 0-ARCH,0-ARCH.26,Implement RRF scoring and fusion,fusion_rag_service.py,Not Started,CRITICAL,2 hours,0-ARCH.24,reciprocal_rank_fusion() function. Combine 4 sources. Calculate RRF scores. Sort top K",
    "PHASE 0-ARCH,0-ARCH.27,Implement re-ranking with CrossEncoder,fusion_rag_service.py,Not Started,HIGH,2 hours,0-ARCH.26,Add CrossEncoder model. Re-rank top 50 to final top 5. Load ms-marco-MiniLM model",
    "PHASE 0-ARCH,0-ARCH.28,Implement query expansion,implementation/retrieval/query_expansion.py,Not Started,MEDIUM,2 hours,0-ARCH.24,Generate 3 query variations. Expand acronyms. Add synonyms. Execute all and merge",
    "PHASE 0-ARCH,0-ARCH.29,Integrate Fusion RAG into langgraph,langgraph_agent.py,Not Started,CRITICAL,2 hours,0-ARCH.27 0-ARCH.6,Replace Pinecone query with Fusion RAG. Update ReAct agent. Add source attribution",
    "PHASE 0-ARCH,0-ARCH.30,Performance test Fusion RAG,Test suite,Not Started,CRITICAL,2 hours,0-ARCH.29,Test keyword semantic hybrid queries. Measure accuracy (+15-25%). Measure latency (<3s)",
]

# Read current file
with open('PROGRESS-TRACKER-WITH-0F.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where to insert (BEFORE Phase 0F, which is after Phase 0E.11)
insert_index = None
for i, line in enumerate(lines):
    if line.startswith('PHASE 0F,0F.1'):
        insert_index = i
        break

if insert_index is None:
    print("ERROR: Could not find insertion point (PHASE 0F,0F.1)")
    exit(1)

# Insert Phase 0-ARCH tasks
new_lines = lines[:insert_index] + [task + '\n' for task in phase_0arch_tasks] + lines[insert_index:]

# Write to new file
with open('PROGRESS-TRACKER-WITH-0ARCH.csv', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Successfully added {len(phase_0arch_tasks)} Phase 0-ARCH tasks!")
print(f"   Inserted at line {insert_index}")
print(f"   New file created: PROGRESS-TRACKER-WITH-0ARCH.csv")
print(f"\nAction required: Rename PROGRESS-TRACKER-WITH-0ARCH.csv to PROGRESS-TRACKER.csv")

print("\nPhase 0-ARCH task groups:")
print("  GROUP 1: Agentic RAG (0-ARCH.1 - 0-ARCH.12) - 12 tasks, 32 hours")
print("  GROUP 2: CRAG Verification (0-ARCH.13 - 0-ARCH.22) - 10 tasks, 22 hours")
print("  GROUP 3: Fusion RAG (0-ARCH.23 - 0-ARCH.30) - 8 tasks, 18 hours")
print("  TOTAL: 30 tasks, 72 hours (~3-4 weeks)")
print("\nThis phase comes BEFORE Phase 0F (system integration)")
