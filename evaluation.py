from pydantic import BaseModel
from openai import OpenAI
import os

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

class Evaluator():
    def __init__(self, name, summary, linkedin):
        self.name = name
        self.summary = summary
        self.linkedin = linkedin
        self.gemini = OpenAI(base_url=os.getenv("GEMINI_BASE_URL"), api_key=os.getenv("GEMINI_API_KEY"))

    def evaluator_system_prompt(self):
        evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
        You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
        The Agent is playing the role of {self.name} and is representing {self.name} on their website. \
        The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
        The Agent has been provided with context on {self.name} in the form of their summary and LinkedIn details. Here's the information:"
        evaluator_system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}"
        evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."
        return evaluator_system_prompt

    def evaluator_user_prompt(self, reply, message, history):
        user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
        user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
        user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
        user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
        return user_prompt

    def evaluate(self, reply, message, history) -> Evaluation:
        print("I'm evaluating")
        messages = [{"role": "system", "content": self.evaluator_system_prompt()}] + [{"role": "user", "content": self.evaluator_user_prompt(reply, message, history)}]
        response = self.gemini.beta.chat.completions.parse(model="gemini-2.0-flash", messages=messages, response_format=Evaluation)
        return response.choices[0].message.parsed