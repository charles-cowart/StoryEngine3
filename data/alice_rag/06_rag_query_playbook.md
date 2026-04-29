# RAG Query Playbook (Alice Collection)

**Document metadata (suggested)**
- work: Alice's Adventures in Wonderland
- doc_type: query_playbook
- chapter_scope: all

## 1) Basic factual query

### User query
"Who are the main figures at the mad tea-party, and what makes that scene bizarre?"

### Target chunks
- Character dossiers: Tea-party cluster.
- Timeline: Chapter 7.
- World rules: time disorder + language governance.

### Expected synthesis shape
- Identify Hatter, March Hare, Dormouse, Alice.
- Explain perpetual tea-time and unresolved riddles.
- Connect social hostility to nonsense discourse.

## 2) Mid-level comparative query

### User query
"Compare the Duchess and Queen of Hearts as authority figures."

### Target chunks
- Character dossiers: Duchess, Queen.
- Themes: Rule systems without reason.
- Timeline: Chapters 6 and 8/11/12.

### Expected synthesis shape
- Duchess: chaotic domestic authoritarianism + hypocrisy.
- Queen: sovereign punitive authoritarianism + theatrical decrees.
- Shared trait: force detached from ethical consistency.

## 3) Advanced interpretive query

### User query
"How does size transformation function as both plot device and identity metaphor?"

### Target chunks
- World rules: size-change mechanics.
- Themes: Identity under transformation.
- Timeline: Chapters 1, 2, 5, 12.

### Expected synthesis shape
- Plot utility: obstacle navigation and scene transitions.
- Symbolic utility: unstable self-concept during maturation.
- Developmental endpoint: agency via voice and judgment.

## 4) Evidence-request query

### User query
"Give textual evidence that Wonderland legal process is absurd."

### Target chunks
- Dialogue evidence bank: trial discourse.
- Timeline: Chapters 11–12.
- World rules: institutional parody.

### Expected synthesis shape
- Summarize procedural irregularities.
- Highlight theatrical handling of evidence.
- Show authority pre-committed to punishment.

## 5) Cross-theme synthesis query

### User query
"How do games and rituals in Wonderland reveal political power?"

### Target chunks
- Themes: games symbol cluster + rule systems theme.
- Timeline: caucus-race, croquet, lobster quadrille.
- World rules: language governance and institutional parody.

### Expected synthesis shape
- Games appear playful but allocate status/obedience.
- Formal rules mask arbitrary enforcement.
- Ritual compliance substitutes for justice.

## 6) Implementation note for LlamaIndex evaluators

When evaluating answer quality, score for:
- **Grounding**: references specific scenes/chapters.
- **Coverage**: pulls at least 2 source files for non-trivial questions.
- **Faithfulness**: avoids invented events.
- **Interpretive coherence**: links evidence to claim explicitly.
