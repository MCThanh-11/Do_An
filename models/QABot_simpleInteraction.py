from together import Together


class ChatBot:
    def __init__(self, api_key):
        """
        Khởi tạo ChatBot với API Key từ Together AI.
        """
        self.api_key = api_key
        self.client = Together(api_key=self.api_key)

    def send_message(self, user_message, system_message="Bạn là một trợ lý AI."):
        """
        Gửi tin nhắn đến mô hình AI và nhận phản hồi.

        :param user_message: Tin nhắn của người dùng.
        :param system_message: Tin nhắn hệ thống để hướng dẫn AI.
        :return: Phản hồi của AI.
        """
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=2048,
                temperature=0.8,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>", "<|eom_id|>"],
                stream=True
            )

            return self.process_response(response)

        except Exception as e:
            return f"Lỗi khi gửi yêu cầu: {e}"

    def process_response(self, response):
        """
        Xử lý phản hồi từ mô hình AI.
        :param response: Dữ liệu phản hồi từ Together AI.
        :return: Nội dung phản hồi dưới dạng chuỗi.
        """
        result = ""
        for token in response:
            if hasattr(token, 'choices'):
                result += token.choices[0].delta.content
                print(token.choices[0].delta.content, end='', flush=True)  # In trực tiếp
        return result