import pandas as pd
import chromadb
import uuid
import os

class Portfolio:
    def __init__(self, file_path=None):
        if file_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))  # this file's directory
            file_path = os.path.join(base_dir, 'resource', 'techstack_portfolios.csv')
        self.file_path = file_path
        self.data = pd.read_csv(self.file_path)

        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name='portfolio')

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                    self.collection.add(documents=row["Techstack"],
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])
                    
    def query_links(self, skills):
         return self.collection.query(query_texts=["Python"], n_results=3)