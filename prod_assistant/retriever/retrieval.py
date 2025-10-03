import os 
from langchain_astradb import AstraDBVectorStore 
from typing import List, Any 
from langchain.core import Document
from utils.config_loader import load_config 
from utils.model_loader import model_loader 
from dotenv import load_dotenv

class Retriever:
    def __init__(self):
        """Summary
        """
        pass 

    def _load_env_variables(self):
        """summary
        """
        pass 

    def load_retriever(self):
        """summary
        """
        pass    

    def call_retriever(self):
        """summary
        """
        pass


if __name__ == "__main__":
    retriever = Retriever()
    user_query = "Can you suggest some good budget laptops?"
    results = retriever.call_retriever(user_query)

    for idx, doc in enumerate(results):
        print(f"Result {idx}: {doc.page_content}\n Metadata: {doc.metadata}\n")