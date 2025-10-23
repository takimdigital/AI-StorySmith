from openai import OpenAI

class ApiClient:
    def __init__(self, base_url="http://localhost:1234/v1", api_key="not-needed", temperature=0.7):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.temperature = temperature

    def call_openai_api(self, messages, model="local-model"):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.temperature,
            )
            content = response.choices[0].message.content
            return content
        except Exception as e:
            print(f"Error calling API: {str(e)}")
            return None
