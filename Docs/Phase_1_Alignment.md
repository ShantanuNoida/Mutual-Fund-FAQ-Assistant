# Phase 1: Sub-Phases & Alignment Check

This document breaks down the implementation of **Phase 1: Data Foundation & Ingestion** into granular sub-phases and verifies how each sub-phase directly aligns with the constraints and objectives set in the `problemstatement.md`.

---

### Sub-Phase 1.1: Corpus Definition & Sourcing
**Description:** Identify the AMC, select diverse schemes, and curate a list of strictly official URLs covering product pages, SIDs, KIMs, Factsheets, and educational material.
*   **Implementation Status:** Completed. Selected HDFC AMC, 5 distinct schemes, and exactly 20 official URLs (HDFC, AMFI, SEBI).
*   **Alignment Check against `problemstatement.md`:** 
    *   ✅ *“Select one Asset Management Company (AMC)”* 
    *   ✅ *“Choose 3–5 mutual fund schemes, ensuring category diversity”* (We chose Mid-Cap, Flexi Cap, Focused 30, ELSS, Top 100 Large Cap).
    *   ✅ *“Collect 15–25 official public URLs... Factsheets, KIM, SID, AMC FAQ, AMFI/SEBI”* 
    *   ✅ *“Use only official public sources... Do not use third-party blogs or aggregator websites.”* (We specifically pivoted away from Groww to strictly use `hdfcfund.com`, `amfiindia.com`, and `sebi.gov.in`).

---

### Sub-Phase 1.2: Data Extraction & Parsing
**Description:** Use Python (`requests`, `beautifulsoup4`, `langchain`) to fetch the content from the 20 official URLs and parse the raw HTML/text into a readable format.
*   **Implementation Status:** Completed via `src/ingestion.py`.
*   **Alignment Check against `problemstatement.md`:**
    *   ✅ *“Answers factual queries about mutual fund schemes”* (The parsed data includes factual data tables, NAVs, and FAQs required to answer queries).
    *   ✅ *Privacy and Security Constraint:* The extraction logic only pulls public data from the AMC. It inherently obeys the rule: *“Do not collect, store, or process PAN or Aadhaar numbers”* as it does not interact with any user data.

---

### Sub-Phase 1.3: Document Chunking & Metadata Tagging
**Description:** Split the extracted, monolithic text into smaller chunks (e.g., 500 tokens). Most importantly, programmatically attach two specific metadata fields to *every* chunk: `Source URL` and `Last Updated Date`.
*   **Implementation Status:** Completed via `RecursiveCharacterTextSplitter` in `src/ingestion.py`.
*   **Alignment Check against `problemstatement.md`:**
    *   ✅ *“Every response must include a source link and last updated date.”* By hardcoding these attributes at the chunk level during ingestion, we guarantee that the LLM in Phase 2 will always have a verifiable citation and date to fulfill the constraint: *“Last updated from sources: <date>”*.

---

### Sub-Phase 1.4: Embedding & Local Vector Storage
**Description:** Convert the tagged chunks into vector embeddings and persist them in a Vector Database for fast semantic retrieval.
*   **Implementation Status:** Completed using local `ChromaDB` and the `all-MiniLM-L6-v2` embedding model.
*   **Alignment Check against `problemstatement.md`:**
    *   ✅ *“Design and implement a lightweight Retrieval-Augmented Generation (RAG)-based assistant”* (Using ChromaDB and local sentence-transformers perfectly aligns with the "lightweight" and standalone requirements).
    *   ✅ *“Accurate retrieval of factual mutual fund information”* (The embeddings allow the system to accurately match user queries to the specific factual chunk).

---

## Conclusion
Every sub-phase of Phase 1 strictly adheres to the data sourcing, privacy, constraint-tagging, and architectural requirements defined in the problem statement. The foundation is properly laid to enforce the "Facts-Only" rules in Phase 2.
