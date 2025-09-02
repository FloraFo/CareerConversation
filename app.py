from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
from tools import Tools
from evaluation import Evaluator
from conversation_log import Log

load_dotenv(override=True)


class Me:

    def __init__(self):
        self.tools = Tools()
        self.conv_logger = Log()
        self.gemini = OpenAI(base_url=os.getenv("GEMINI_BASE_URL"), api_key=os.getenv("GEMINI_API_KEY"))
        self.name = "Filomena Forina"
        self.github = "https://github.com/FloraFo"
        reader = PdfReader("me/filoCV.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()
        self.evaluator = Evaluator(self.name, self.summary, self.linkedin)

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = getattr(self.tools, tool_name, None)
            result = tool(**arguments) if tool else {}
            print(f"Tool result: {result}", flush=True)
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, "
        prompt += f"particularly questions related to {self.name}'s career, background, skills and experience. "
        prompt += f"Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. "
        prompt += f"You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. "
        prompt += f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
        prompt += f"If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. "
        prompt += f"If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "
        prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n## GitHub Profile:\n{self.github}"
        prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return prompt

    def rerun(self, reply, message, history, feedback):
        system_prompt = self.system_prompt()
        updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
        updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
        updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
        messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
        response = self.gemini.chat.completions.create(model="gemini-2.5-flash-preview-05-20", messages=messages)
        return response.choices[0].message.content

    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.gemini.chat.completions.create(model="gemini-2.5-flash-preview-05-20", messages=messages, tools=self.tools.tools_func)
            if response.choices[0].finish_reason == "tool_calls":
                msg = response.choices[0].message
                tool_calls = msg.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(msg)
                messages.extend(results)
                reply = response.choices[0].message.content
            else:
                reply = response.choices[0].message.content
                evaluation = self.evaluator.evaluate(reply, message, history)
                if evaluation.is_acceptable:
                    print('Passed evaluation')
                else:
                    print('Failed evaluation')
                    print(evaluation.feedback)
                    reply = self.rerun(reply, message, history, evaluation.feedback)
                done = True
        self.conv_logger.log_answer(question=message, answer=reply)
        return reply
    

if __name__ == "__main__":
    me = Me()
    gr.ChatInterface(fn=me.chat, title="Career Conversation with Filomena Forina", type="messages").launch()
    