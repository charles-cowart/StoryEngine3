# Alice in Wonderland RAG Collection Guide

This folder is a **story-grade retrieval corpus** for building a LlamaIndex RAG system around *Alice’s Adventures in Wonderland*.

It is intentionally designed as a practical dataset rather than a “hello world” sample:

- It separates narrative text from analysis and ontology-like references.
- It uses retrieval-oriented writing patterns (clear sectioning, explicit entities, and query hooks).
- It includes source-aware metadata blocks that can be parsed and attached to nodes.
- It contains synthetic-but-grounded “critical interpretation” notes to support higher-order questions.

## File map

- `01_narrative_timeline.md` – chapter-by-chapter timeline with pivotal events and retrieval anchors.
- `02_character_dossiers.md` – detailed character cards (traits, motivations, evidence scenes, relationships).
- `03_world_rules_and_logic.md` – setting logic, language play, identity instability, and absurdity mechanics.
- `04_dialogue_evidence_bank.md` – curated dialogue snippets and paraphrased evidence for quote-style retrieval.
- `05_themes_symbols_and_motifs.md` – thematic lenses with scene-level anchors.
- `06_rag_query_playbook.md` – realistic user questions and expected retrieval targets.

## Suggested metadata fields per document

Use the following metadata when indexing with `SimpleDirectoryReader` or custom node parsers:

- `work`: `Alice's Adventures in Wonderland`
- `collection`: `alice_rag`
- `doc_type`: one of `timeline`, `character`, `world_rules`, `dialogue_bank`, `themes`, `query_playbook`
- `chapter_scope`: e.g., `1-3`, `7`, `all`
- `entities`: comma-separated list of major entities
- `difficulty`: e.g., `basic`, `intermediate`, `advanced` (for reranking / routing)

## Chunking recommendations

For a dense story corpus, prioritize semantic coherence:

1. Split on markdown headings (`##` / `###`) first.
2. Use chunk sizes around **500–900 tokens** with **80–150 overlap**.
3. Keep character cards intact where possible (don’t split tiny files).
4. Add title-aware metadata so each chunk retains the section path.

## Why this corpus works for real RAG

A realistic story RAG must support:

- **Factoid lookup** (“Who attended the tea party?”)
- **Cross-scene synthesis** (“How does size change shape identity conflict?”)
- **Comparative interpretation** (“Duchess vs. Queen on authority?”)
- **Evidence-backed answers** with chapter-grounded references.

This collection is built to support all four modes.
