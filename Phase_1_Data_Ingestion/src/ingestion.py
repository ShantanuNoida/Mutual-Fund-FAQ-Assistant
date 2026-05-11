import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import Chroma



# Configuration
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'chroma_db')
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

URLS = [
    # Scheme Product Pages (Corrected path: /explore/mutual-funds/)
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-mid-cap-opportunities-fund/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-flexi-cap-fund/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-focused-30-fund/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-elss-tax-saver-fund/direct",
    "https://www.hdfcfund.com/explore/mutual-funds/hdfc-top-100-fund/direct",
    
    # Official Document Portals
    "https://www.hdfcfund.com/investor-desk/downloads/scheme-information-document-sid",
    "https://www.hdfcfund.com/investor-desk/downloads/key-information-memorandum-kim",
    "https://www.hdfcfund.com/investor-desk/downloads/factsheets",
    
    # HDFC General FAQs
    "https://www.hdfcfund.com/faqs",
    
    # AMFI Knowledge Centre (Corrected dynamic URLs)
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=IntroductionMutualFunds",
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=NetAssetValueNAV",
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=expenseRatio",
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=sip",
    "https://www.amfiindia.com/investor/knowledge-center-info?zoneName=TaxationMutualFunds"
]

def clean_html(html_content, url):
    """Strips headers, footers, scripts, and styles to extract clean text."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove noise tags
    for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form", "noscript"]):
        tag.decompose()
        
    # Target specific content areas if known
    content_area = None
    if "hdfcfund.com" in url:
        # HDFC specific content container
        content_area = soup.find(id="main-content") or soup.find(class_="product-details-content")
    elif "amfiindia.com" in url:
        # AMFI specific content container
        content_area = soup.find(id="divContent") or soup.find(class_="knowledge-center-detail")

    # Fallback to body or general main
    if not content_area:
        content_area = soup.find("main") or soup.find(id="main") or soup.find(class_="content") or soup.body

    if not content_area:
        return ""
        
    # Get text and clean whitespace
    text = content_area.get_text(separator="\n")
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    
    return text

def load_documents():
    """Loads documents from the official URLs using targeted cleaning."""
    print("Loading and cleaning documents from official URLs...")
    docs = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for url in URLS:
        try:
            # Add a small delay to avoid rate limits
            import time
            time.sleep(1)
            
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            
            cleaned_text = clean_html(response.text, url)
            
            if cleaned_text and len(cleaned_text) > 100:
                doc = Document(
                    page_content=cleaned_text,
                    metadata={
                        "Source URL": url,
                        "Last Updated Date": datetime.now().strftime("%Y-%m-%d")
                    }
                )
                docs.append(doc)
                print(f"[SUCCESS] Scraped & Cleaned ({len(cleaned_text)} chars): {url}")
            else:
                print(f"[WARNING] Content too thin or empty for: {url}")
                
        except Exception as e:
            print(f"[ERROR] Failed to scrape {url}: {e}")
            
    return docs

def chunk_documents(docs):
    """Splits documents into larger chunks with more overlap to preserve context."""
    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, # Further increased for better table preservation
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def store_in_chroma(chunks):
    """Uses HF Inference API to embed the chunks and stores them in Chroma."""
    print(f"Initializing HF Inference API for model 'sentence-transformers/all-MiniLM-L6-v2'...")
    embeddings = HuggingFaceEndpointEmbeddings(
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        model="sentence-transformers/all-MiniLM-L6-v2"
    )


    
    # Clear existing DB to ensure fresh start
    import shutil
    if os.path.exists(CHROMA_DB_DIR):
        print(f"Clearing existing database at {CHROMA_DB_DIR}...")
        shutil.rmtree(CHROMA_DB_DIR)
        
    print(f"Storing chunks in ChromaDB at: {CHROMA_DB_DIR}")
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    vectorstore.persist()
    print("Vector database successfully populated and persisted!")

def main():
    # 1. Load from Web
    docs = load_documents()
    
    # 2. Load from local verified data (Fallback/High-Quality source)
    local_data_path = os.path.join(os.path.dirname(__file__), "official_fund_data.txt")
    if os.path.exists(local_data_path):
        print(f"Loading verified local data from {local_data_path}...")
        with open(local_data_path, "r", encoding="utf-8") as f:
            content = f.read()
            doc = Document(
                page_content=content,
                metadata={
                    "Source URL": "Official HDFC/AMFI Documents (Verified)",
                    "Last Updated Date": datetime.now().strftime("%Y-%m-%d")
                }
            )
            docs.append(doc)
            
    if not docs:
        print("No documents loaded. Check network or URLs.")
        return
        
    chunks = chunk_documents(docs)
    store_in_chroma(chunks)

if __name__ == "__main__":
    main()
