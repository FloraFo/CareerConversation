import csv
from datetime import datetime

class Log():
    def __init__(self):
        # Use Hugging Face Spaces persistent storage and make file private
        self.filename = "/data/.conversation.csv"

    def log(self, message):
        with open(self.filename, "a") as f:
            f.write(f"{datetime.now()}: {message}\n")

    def log_answer(self, question=None, answer=None):
        """
        Stores the provided data in a CSV file with columns: date,  question, answer.
        """
        import re

        def strip_markdown(text):
            if text is None:
                return ""
            # Remove markdown formatting
            # Remove code blocks
            text = re.sub(r'```[\s\S]*?```', '', text)
            # Remove inline code
            text = re.sub(r'`([^`]*)`', r'\1', text)
            # Remove bold/italic/strikethrough
            text = re.sub(r'([*_~]{1,3})(\S.*?\S)\1', r'\2', text)
            # Remove links but keep text
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
            # Remove images but keep alt text
            text = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', r'\1', text)
            # Remove headings
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
            # Remove blockquotes
            text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
            # Remove unordered/ordered list markers
            text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
            text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
            # Remove horizontal rules
            text = re.sub(r'^---$', '', text, flags=re.MULTILINE)
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        def wrap_text(text):
            if text is None:
                return ""
            return str(text)

        row = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": wrap_text(question),
            "answer": strip_markdown(answer)
        }
        file_exists = False
        try:
            with open(self.filename, "r", newline='', encoding='utf-8') as f:
                file_exists = True
        except FileNotFoundError:
            pass
        with open(self.filename, "a", newline='', encoding='utf-8') as csvfile:
            fieldnames = ["date", "question", "answer"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)