from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


class PDFHandler:
    def __init__(self, document_path):
        self.path = document_path

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            is_separator_regex=False 
        )


    def load_and_split(self):
        loader = PyPDFLoader(self.path)
        pages = loader.load()
        chunks = []
        
        # Get fileName for metadata
        file_name = os.path.basename(self.path)

        for page in pages:
            text = page.page_content
            # Split text into pieces
            pieces = self.text_splitter.create_documents([text])
            # Add metadata to each piece
            for piece in pieces:
                piece.metadata["source"] = file_name
            chunks.extend(pieces)

        return chunks 
    



