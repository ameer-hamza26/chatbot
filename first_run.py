from pdf_handler import PDFHandler
from vector_db import VectorDatabase
import os

def ingest_pdf(pdf_path, vector_db):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return
        
    file_name = os.path.basename(pdf_path)
    
    # Check if already present
    if vector_db.is_document_present(file_name):
        print(f"Skipping {file_name}: Documents already present in RAG system.")
        return
    
    print(f"Extraction and embedding step started for: {file_name}")
    
    try:
        pdf_handler = PDFHandler(document_path=pdf_path)
        documents = pdf_handler.load_and_split()
        vector_db.add_documents(documents=documents)
        print(f"Successfully indexed {file_name}.")
    except Exception as e:
        print(f"Error indexing {file_name}: {e}")

# Initialize vector database
vector_db = VectorDatabase()

# List of PDFs to index
pdfs_to_index = [
    "./tkr.pdf"
]

# Process each PDF
for pdf in pdfs_to_index:
    ingest_pdf(pdf, vector_db)

# Now searching in vector db to verify
print("\nVerifying index with a test query...")
query = "What is TKR Restaurant and what menu items does it offer?"
results = vector_db.search(query_text=query, docs_to_search=3)

for i, doc in enumerate(results):
    source = doc.metadata.get('source', 'Unknown')
    print(f"Result {i+1} (Source: {source}):\n{doc.page_content[:200]}...\n")
