# Phase 2: Sub-Phases & Alignment Check

This document breaks down the implementation of **Phase 2: Core RAG Pipeline** into granular sub-phases and verifies how each sub-phase directly adheres to the strict constraints and objectives set in the `problemstatement.md`.

---

### Sub-Phase 2.1: Retrieval Engine & Context Assembly
**Description:** Connects to the local ChromaDB populated in Phase 1. When a user asks a question, it embeds the query, searches for the Top-K most relevant document chunks, and formats them into a clean context string alongside their `Source URL`.
*   **Implementation Status:** Completed in `rag_engine.py` using `langchain_community.vectorstores.Chroma`.
*   **Alignment Check against `problemstatement.md`:** 
    *   ✅ *“Accurate retrieval of factual mutual fund information”* 
    *   ✅ *“Uses a curated corpus of official documents”* (Because the Retriever strictly searches only the `chroma_db` populated with official HDFC/AMFI/SEBI data, it is impossible for it to fetch third-party blog data).

---

### Sub-Phase 2.2: LLM Configuration & Safety Parameters
**Description:** Integration of the Large Language Model (`llama-3.1-8b-instant` via Groq) to process the context and generate human-readable text. The model is specifically configured with `temperature=0`.
*   **Implementation Status:** Completed via `ChatGroq`.
*   **Alignment Check against `problemstatement.md`:**
    *   ✅ *“Prioritizes accuracy over intelligence”*
    *   ✅ *“Without any advisory bias or speculative content”* (By setting `temperature=0`, we remove the LLM's creativity and randomness, forcing it to behave purely deterministically and strictly report facts without hallucinating).

---

### Sub-Phase 2.3: Prompt Engineering & Mathematical Constraints
**Description:** The heart of the Phase 2 pipeline. The LLM is bound by a strict System Prompt (`PROMPT_TEMPLATE`) that dictates exactly what it can and cannot say.
*   **Implementation Status:** Completed. The prompt strictly instructs the LLM on behavior and formatting.
*   **Alignment Check against `problemstatement.md`:**
    *   ✅ *“Each response is limited to a maximum of 3 sentences”* (Enforced directly via the prompt rule: `Your answer MUST be exactly 3 sentences or fewer.`).
    *   ✅ *“Each response includes exactly one citation link”* (Enforced via the prompt rule: `You MUST include exactly one citation link at the very end... taken directly from the Source URL`).
    *   ✅ *“No investment advice or recommendations”* & *“No performance comparisons or return calculations”* (Enforced via `CONSTRAINTS 1 and 2` in the prompt, instructing the model to never opine or calculate).
    *   ✅ *“Strict adherence to facts-only responses”* (Enforced by instructing the model: `If the answer is not in the context, say exactly: 'I couldn't find verified information regarding your query in the official documents.'`).

---

## Conclusion
Phase 2 relies heavily on **Prompt Engineering** and **Deterministic Model Configuration** (`temp=0`) to fulfill the formatting and content constraints. 

While Phase 2 handles these beautifully at the LLM generation stage, we will solidify this compliance in **Phase 3 (Guardrails & Post-Processing)** by adding hardcoded programmatic checks (like python `len(sentences) <= 3`) to ensure that even if the LLM disobeys the prompt, the final output to the user remains strictly compliant.
