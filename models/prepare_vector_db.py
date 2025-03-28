import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GPT4AllEmbeddings

class VectorDBProcess():
    def __init__(self):
        # super().__init__()
        # self.vector_db_path =  "../vectorstorage/db_faiss"
        pass
    @staticmethod
    def create_db_from_files(self):
        # loader = DirectoryLoader(self,loader_cls=PyPDFLoader)
        # documents = loader.load()

        loader = PyPDFLoader(self)
        documents = loader.load()
        """
        if os.path.isfile(self):
            # Handle single file case
            loader = PyPDFLoader(self)
            documents = loader.load()
        elif os.path.isdir(self):
            # Handle directory case
            loader = DirectoryLoader(self, glob="*.pdf", loader_cls=PyPDFLoader)
            documents = loader.load()
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        print(chunks[0])

        embedding_model = GPT4AllEmbeddings(model_file="../lbs/all-MiniLM-L6-v2-f16.gguf")
        print(embedding_model)

        db = FAISS.from_documents(chunks, embedding_model)
        print(db)

        db.save_local("../vectorstorage/db_faiss")
        return db
##############
""""
if __name__ == "__main__":
    vector_db_processor = VectorDBProcess()
    db = vector_db_processor.create_db_from_files("../data/K224040496-Mai.pdf")  # Thay đổi đường dẫn tùy theo file của bạn
"""
    # print("Cơ sở dữ liệu vector FAISS đã được tạo và lưu trữ tại:", vector_db_processor.vector_db_path)
