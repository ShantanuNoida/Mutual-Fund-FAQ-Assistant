import re

# ==========================================
# 1. PII Filtering (Pre-processing)
# ==========================================

# Regex Patterns for sensitive data
PII_PATTERNS = {
    "PAN": r"\b[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}\b",
    "Aadhaar": r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
    "Generic_Account_or_OTP": r"\b\d{6,18}\b"
}

def check_pii(query: str) -> dict:
    """Checks the query against PII patterns. Returns a dict with status and message."""
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, query):
            return {
                "blocked": True,
                "reason": "PII_DETECTED",
                "message": f"Privacy Warning: Your query appears to contain sensitive information ({pii_type}). We do not process or store PAN, Aadhaar, account numbers, or OTPs. Please rephrase your query without personal details."
            }
    return {"blocked": False}


# ==========================================
# 2. Intent & Performance Filtering
# ==========================================

ADVISORY_KEYWORDS = [
    "should i", "which is better", "recommend", "advice", 
    "invest in", "best fund", "good investment", "compare"
]

PERFORMANCE_KEYWORDS = [
    "return", "performance", "cagr", "yield", "growth", "profit"
]

def check_intent(query: str) -> dict:
    """Checks if the query violates the facts-only or no-performance constraint."""
    query_lower = query.lower()
    
    for word in ADVISORY_KEYWORDS:
        if word in query_lower:
            return {
                "blocked": True,
                "reason": "ADVISORY",
                "message": "I can only provide factual details. Facts-only. No investment advice.\nFor educational resources on how to choose a mutual fund, please visit: https://www.amfiindia.com/investor-corner/knowledge-center/what-are-mutual-funds.html"
            }
            
    for word in PERFORMANCE_KEYWORDS:
        if word in query_lower:
            return {
                "blocked": True,
                "reason": "PERFORMANCE",
                "message": "For performance-related queries and historical returns, please refer strictly to the official factsheet: https://www.hdfcfund.com/investor-desk/downloads/factsheets"
            }
            
    return {"blocked": False}


# ==========================================
# 3. Post-Processing Formatting
# ==========================================

def enforce_sentence_limit(text: str, max_sentences: int = 3) -> str:
    """Splits text into sentences and truncates to max_sentences."""
    # Basic sentence split by punctuation followed by space
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    if len(sentences) <= max_sentences:
        return text
        
    truncated = " ".join(sentences[:max_sentences])
    if not truncated.endswith((".", "!", "?")):
        truncated += "."
    return truncated

def inject_footer(text: str, date_string: str) -> str:
    """Appends the required footer."""
    footer = f"\n\nLast updated from sources: {date_string}"
    if footer not in text:
        return text + footer
    return text
