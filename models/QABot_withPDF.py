import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.embeddings import Embeddings
from together import Together


class QABot:
    def __init__(self, api_key, vector_db_path):
        """
        Khởi tạo ChatBot sử dụng Together AI và FAISS Vector DB.
        """
        self.api_key = api_key
        self.client = Together(api_key=self.api_key)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2")  # Load embeddings
        self.db = self.load_vector_db(vector_db_path)
        self.prompt = self.create_prompt()

    def load_vector_db(self, vector_db_path):
        """Tải vector database từ FAISS."""
        return FAISS.load_local(
            vector_db_path,
            self.embedding_model,
            allow_dangerous_deserialization=True
        )

    def create_prompt(self):
        """Tạo template prompt."""
        template = """
        <|im_start|>system
        Bạn là một trợ lý AI. Sử dụng thông tin sau để trả lời câu hỏi của người dùng. Nếu không biết, hãy nói 'Tôi không biết'.
        {context}
        <|im_end|>
        <|im_start|>user
        {question}
        <|im_end|>
        <|im_start|>assistant
        """
        return PromptTemplate(template=template, input_variables=["context", "question"])

    def retrieve_context(self, question):
        """Tìm kiếm ngữ cảnh từ VectorDB."""
        retriever = self.db.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(question)
        context_list = []
        for doc in docs:
            context_list.append(doc.page_content)
        context = "\n".join(context_list)
        return context if context else "Không có thông tin phù hợp."

    def send_message(self, user_message, context):
        """
        Gửi tin nhắn đến mô hình AI và nhận phản hồi.
        """
        system_message = "Sử dụng thông tin sau để trả lời câu hỏi của người dùng."
        full_prompt = self.prompt.format(context=context, question=user_message)

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1024,
                temperature=0.3,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1.3,
                stop=["<|eot_id|>", "<|eom_id|>"],
                stream=True
            )
            return self.process_response(response)

        except Exception as e:
            return f"Lỗi khi gửi yêu cầu: {e}"

    def process_response(self, response):
        """
        Xử lý phản hồi từ mô hình AI.
        """
        result = ""
        for token in response:
            if hasattr(token, 'choices'):
                result += token.choices[0].delta.content
                print(token.choices[0].delta.content, end='', flush=True)  # In trực tiếp
        return result

    def get_answer(self, question):
        """Trả lời câu hỏi dựa trên Vector DB và Together AI."""
        context = self.retrieve_context(question)
        return self.send_message(question, context)
"""
# Chạy thử chương trình
if __name__ == "__main__":
    api_key = "7cfc08f9f0266495db28836e118354831597ff6ca7e81342469e410b68293d9a"  # Thay thế bằng API Key thực tế
    vector_db_path = "../vectorstorage/db_faiss"

    bot = QABot(api_key, vector_db_path)
    question = "Nội dung sách là gì?"
    response = bot.get_answer(question)

    print(response)
"""