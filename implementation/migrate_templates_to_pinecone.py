"""
Migrate Templates to Pinecone - Data-Driven Architecture
=========================================================

Move all hardcoded templates from thought_prompts.py to Pinecone database.
After this migration, all templates will be data-driven from Pinecone.

This script migrates:
1. 6 Reasoning templates (CODE_ERROR, INFRA_ERROR, CONFIG_ERROR, etc.)
2. 10 Few-shot examples (2 per category)
3. 1 Observation template (global)
4. 1 Answer generation template (global)

Usage:
    python migrate_templates_to_pinecone.py

Environment Variables Required:
    PINECONE_API_KEY - Pinecone API key
    OPENAI_API_KEY - OpenAI API key

File: implementation/migrate_templates_to_pinecone.py
Created: 2025-11-01
"""

import sys
import os
from datetime import datetime
from typing import List

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add paths
implementation_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, implementation_dir)
agents_dir = os.path.join(implementation_dir, 'agents')
sys.path.insert(0, agents_dir)

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# Import existing templates (last time we use these hardcoded ones!)
# Direct import to avoid langgraph dependency
import importlib.util
spec = importlib.util.spec_from_file_location("thought_prompts", os.path.join(agents_dir, "thought_prompts.py"))
thought_prompts_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thought_prompts_module)
ThoughtPrompts = thought_prompts_module.ThoughtPrompts

load_dotenv()


def create_dummy_embedding() -> List[float]:
    """Minimal vector - templates queried by metadata, not similarity"""
    return [0.01] * 1536  # Pinecone rejects all-zero vectors


def migrate_reasoning_templates(index) -> int:
    """Migrate 6 reasoning templates to Pinecone"""
    print("\n[1/4] Migrating Reasoning Templates...")
    count = 0

    for category, template_content in ThoughtPrompts._FALLBACK_REASONING_TEMPLATES.items():
        vector_id = f"template_reasoning_{category}"

        metadata = {
            "doc_type": "reasoning_template",
            "template_type": "REASONING",
            "error_category": category,
            "template_content": template_content,
            "placeholders": "error_info,context_summary",
            "version": "1.0",
            "active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "text": f"Reasoning template for {category}"  # LangChain needs this
        }

        index.upsert(vectors=[{
            "id": vector_id,
            "values": create_dummy_embedding(),
            "metadata": metadata
        }])

        print(f"  ✓ {category:20s} ({len(template_content):4d} chars)")
        count += 1

    print(f"✅ Migrated {count} reasoning templates")
    return count


def migrate_few_shot_examples(index) -> int:
    """Migrate 10 few-shot examples to Pinecone"""
    print("\n[2/4] Migrating Few-Shot Examples...")
    count = 0

    for category, examples in ThoughtPrompts._FALLBACK_FEW_SHOT_EXAMPLES.items():
        print(f"\n  [{category}]")

        for idx, example in enumerate(examples, 1):
            vector_id = f"template_fewshot_{category}_{idx}"

            metadata = {
                "doc_type": "few_shot_example",
                "template_type": "FEW_SHOT",
                "error_category": category,
                "example_index": idx,
                "error_summary": example.error_summary,
                "thought": example.thought,
                "action": example.action,
                "reasoning": example.reasoning,
                "version": "1.0",
                "active": True,
                "created_at": datetime.utcnow().isoformat(),
                "text": f"Few-shot example {idx} for {category}"  # LangChain needs this
            }

            index.upsert(vectors=[{
                "id": vector_id,
                "values": create_dummy_embedding(),
                "metadata": metadata
            }])

            print(f"    ✓ Example {idx}")
            count += 1

    print(f"\n✅ Migrated {count} few-shot examples")
    return count


def migrate_observation_template(index) -> int:
    """Migrate observation template to Pinecone"""
    print("\n[3/4] Migrating Observation Template...")

    vector_id = "template_observation_global"

    metadata = {
        "doc_type": "observation_template",
        "template_type": "OBSERVATION",
        "error_category": "GLOBAL",
        "template_content": ThoughtPrompts._FALLBACK_OBSERVATION_TEMPLATE,
        "placeholders": "tool_name,tool_results,current_confidence",
        "version": "1.0",
        "active": True,
        "created_at": datetime.utcnow().isoformat(),
        "text": "Observation analysis template (global)"  # LangChain needs this
    }

    index.upsert(vectors=[{
        "id": vector_id,
        "values": create_dummy_embedding(),
        "metadata": metadata
    }])

    print(f"  ✓ Observation template")
    print(f"✅ Migrated observation template")
    return 1


def migrate_answer_generation_template(index) -> int:
    """Migrate answer generation template to Pinecone"""
    print("\n[4/4] Migrating Answer Generation Template...")

    vector_id = "template_answer_generation_global"

    metadata = {
        "doc_type": "answer_generation_template",
        "template_type": "ANSWER_GENERATION",
        "error_category": "GLOBAL",
        "template_content": ThoughtPrompts._FALLBACK_ANSWER_GENERATION_TEMPLATE,
        "placeholders": "error_category,all_context,reasoning_history",
        "version": "1.0",
        "active": True,
        "created_at": datetime.utcnow().isoformat(),
        "text": "Answer generation template (global)"  # LangChain needs this
    }

    index.upsert(vectors=[{
        "id": vector_id,
        "values": create_dummy_embedding(),
        "metadata": metadata
    }])

    print(f"  ✓ Answer generation template")
    print(f"✅ Migrated answer generation template")
    return 1


def verify_migration(embeddings):
    """Verify all templates in Pinecone"""
    print("\n[VERIFICATION] Checking Pinecone...")

    vectorstore = PineconeVectorStore(
        index_name="ddn-knowledge-docs",
        embedding=embeddings,
        pinecone_api_key=os.getenv("PINECONE_API_KEY")
    )

    checks = [
        ("reasoning_template", "Reasoning Templates", 6),
        ("few_shot_example", "Few-Shot Examples", 6),  # CODE_ERROR has 2, others have 1 each
        ("observation_template", "Observation Template", 1),
        ("answer_generation_template", "Answer Generation Template", 1)
    ]

    all_good = True

    for doc_type, name, expected in checks:
        docs = vectorstore.similarity_search(
            "template",
            k=100,
            filter={"doc_type": doc_type, "active": True}
        )
        actual = len(docs)
        status = "✅" if actual == expected else "⚠️"
        print(f"{status} {name:30s} Expected: {expected:2d}  Found: {actual:2d}")
        if actual != expected:
            all_good = False

    return all_good


def main():
    print("\n" + "=" * 70)
    print(" MIGRATE TEMPLATES TO PINECONE - DATA-DRIVEN ARCHITECTURE")
    print("=" * 70)

    # Check environment
    if not os.getenv("PINECONE_API_KEY"):
        print("❌ ERROR: PINECONE_API_KEY not found")
        return 1

    # Connect to Pinecone
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("ddn-knowledge-docs")
        print("✅ Connected to Pinecone: ddn-knowledge-docs")
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return 1

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        dimensions=1536
    )

    # Run migrations
    total = 0
    total += migrate_reasoning_templates(index)
    total += migrate_few_shot_examples(index)
    total += migrate_observation_template(index)
    total += migrate_answer_generation_template(index)

    # Verify
    if verify_migration(embeddings):
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETE - ALL TEMPLATES NOW IN PINECONE")
        print("=" * 70)
        print(f"\nMigrated {total} templates total")
        print("\nNext:")
        print("  1. Update thought_prompts.py to fetch from Pinecone")
        print("  2. Remove hardcoded templates from code")
        print("  3. Add caching for performance")
        print("  4. Test everything works")
        return 0
    else:
        print("\n⚠️  VERIFICATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
