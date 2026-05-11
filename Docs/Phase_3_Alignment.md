# Phase 3: Sub-Phases & Alignment Check

This document breaks down the implementation of **Phase 3: Guardrails, Refusal & Post-Processing** into granular sub-phases and verifies how each sub-phase directly adheres to the strict constraints and objectives set in the `problemstatement.md`.

---

### Sub-Phase 3.1: Pre-processing PII Guardrails
**Description:** Implemented a regex-based scanner that intercepts the user's query *before* it is embedded or sent to the LLM. It detects patterns for PAN cards, Aadhaar numbers, and generic account/OTP sequences.
*   **Implementation Status:** Completed in `guardrails.py` using `re.search`.
*   **Alignment Check against `problemstatement.md`:** 
    *   ✅ *“Do not collect, store, or process PAN or Aadhaar numbers.”* By blocking these at the input stage, the system ensures that sensitive user data never touches the LLM (Groq) or the persistent Vector DB, maintaining absolute privacy.

---

### Sub-Phase 3.2: Intent Classification & Automated Refusal
**Description:** A keyword-based engine that identifies "Advisory" or "Performance" intent. If a user asks for recommendations ("Which is better?") or returns ("What is the CAGR?"), the RAG pipeline is bypassed, and a standard, compliant refusal is returned.
*   **Implementation Status:** Completed in `guardrails.py`.
*   **Alignment Check against `problemstatement.md`:**
    *   ✅ *“No investment advice or recommendations.”* 
    *   ✅ *“No performance comparisons or return calculations.”*
    *   ✅ *“Without any advisory bias or speculative content.”* (This sub-phase acts as a hard programmatic wall that prevents the LLM from even attempting to answer subjective or performance-based queries).

---

### Sub-Phase 3.3: Programmatic Post-Processing
**Description:** A final layer that audits the LLM's output. It programmatically splits the text into sentences to enforce the 3-sentence limit and appends a standardized "Last updated" footer.
*   **Implementation Status:** Completed via `SafeRAGEngine` in `safe_rag_pipeline.py`.
*   **Alignment Check against `problemstatement.md`:**
    *   ✅ *“Each response is limited to a maximum of 3 sentences.”* (Using Python's `re.split` to truncate ensures that even if the LLM generates a long response, the user only sees a compliant 3-sentence output).
    *   ✅ *“Every answer must include a... last updated date.”* (By programmatically injecting the date footer, we guarantee this constraint is met for every single factual query).

---

## Conclusion
Phase 3 serves as the "Safety Envelope" for the assistant. While Phase 2 relies on LLM "instruction following," Phase 3 uses **deterministic code** to guarantee compliance with the most sensitive legal and formatting constraints in the problem statement.
