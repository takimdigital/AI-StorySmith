import os
from .api_client import ApiClient

class UserInteraction:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_user_feedback(self, content_type, content, context="", component_name=None):
        """Prompt the user for feedback on the generated content."""
        print(f"\n🧐 Here's the {content_type} we've crafted for you:\n")
        print(content)

        feedback = input(f"\n🤔 Thoughts on this {content_type}? If you have feedback or want a revision, let us know. Otherwise, type 'perfect' to move on: ").strip().lower()

        if feedback == 'perfect':
            if component_name:
                feedback_file_path = os.path.join('feedback_files', f'{component_name}_feedback.txt')
                if os.path.exists(feedback_file_path):
                    os.remove(feedback_file_path)
            return content
        else:
            print("\n🕵️‍♂️ Alright, let's sprinkle some more magic on this!")
            return self.revise_content(content, feedback, context, component_name)

    def revise_content(self, original_content, feedback, context, component_name=None):
        prompt_content = [
            {
                "role": "system",
                "content": "You are a meticulous revision specialist, skilled in refining content based on feedback. Your primary goal is to enhance the original content while preserving its core essence. It's crucial to avoid chatbot-like behavior and only focus on the task of revision."
            },
            {
                "role": "user",
                "content": f"Given the detailed feedback: '{feedback}', and the context: '{context}', adeptly refine the following content without straying from the feedback's intent: '{original_content}'. Ensure the revised content is clear and concise without any additional commentary."
            }
        ]

        revised_content = self.api_client.call_openai_api(prompt_content)

        if component_name:
            feedback_file_path = os.path.join('feedback_files', f'{component_name}_feedback.txt')
            os.makedirs('feedback_files', exist_ok=True)
            with open(feedback_file_path, 'w', encoding='utf-8') as file:
                file.write(revised_content)

        return revised_content
