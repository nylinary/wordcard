import abc
import re

from django.conf import settings
from gigachat import GigaChat
from openai import OpenAI


class BaseLinguisticModel(abc.ABC):
    """Абстрактный класс для работы с различными API для получения определений слов."""

    @abc.abstractmethod
    def get_word_definition(self, word: str) -> dict:
        """Получить определение слова."""
        pass

    @abc.abstractmethod
    def get_word_examples(self, word: str) -> list:
        """Получить примеры использования слова."""
        pass

    @abc.abstractmethod
    def generate_quiz_options(self, word: str) -> dict:
        """Сгенерировать вопрос и варианты ответов для квиза."""
        pass


class DeepSeekLinguisticModel(BaseLinguisticModel):
    """Реализация для API DeepSeek."""

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_API_BASE_URL
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def get_word_definition(self, word: str) -> dict:
        prompt = f"""
            You are an assistant helping English learners. 
            Define the word: '{word}' in clear English.
            Do not include any formatting, titles, or markdown. Return plain text only.
            Avoid any extra phrases, introductions, or conclusions. Just the definition.
            """
        completion = self.client.chat.completions.create(
            extra_body={}, model="deepseek/deepseek-r1:free", messages=[{"role": "user", "content": prompt}]
        )
        return {"word": word, "part_of_speech": "", "definition": completion.choices[0].message.content}

    def get_word_examples(self, word: str) -> list:
        prompt = f"""
            You are an assistant helping English learners. 
            Give 2-3 examples of how the word '{word}' is used in real sentences.
            Do not include any formatting, titles, or markdown. Return plain text only.
            Avoid extra text like 'Here are examples' — just return the sentences.
            """
        completion = self.client.chat.completions.create(
            extra_body={}, model="deepseek/deepseek-r1:free", messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.split("\n")

    def generate_quiz_options(self, word: str) -> dict:
        # Заполним моковыми данными
        return {
            "question": f"What does the word '{word}' mean?",
            "correct_answer": f"Definition of '{word}'",
            "options": [
                f"Definition of '{word}'",
                "Incorrect definition 1",
                "Incorrect definition 2",
                "Incorrect definition 3",
            ],
        }


class GigaChatModel(BaseLinguisticModel):
    def __init__(self):
        self.giga = GigaChat(credentials=settings.GIGACHAT_AUTH_KEY, verify_ssl_certs=False)

    def get_word_definition(self, word: str) -> dict:
        prompt = f"""
        You are an assistant helping English learners.
        Define the word or phrase: '{word}' in clear and simple English.
        Return plain text only. Do not include any explanations, examples, markdown, numbering, or titles.
        Just return the definition as one plain paragraph.
        """
        response = self.giga.chat(prompt)
        return {"word": word, "part_of_speech": "", "definition": response.choices[0].message.content.strip()}

    def get_word_examples(self, word: str) -> list:
        prompt = f"""
        You are an assistant helping English learners.
        Return exactly 2 example sentences showing how the word or phrase '{word}' is used.
        Do not explain them. Do not include markdown or extra text.
        Just return the two sentences, each on its own line.
        Example format:
        I need to get over my fear of heights before I can go skydiving.
        She's trying to get over her ex-boyfriend.
        """
        response = self.giga.chat(prompt)
        return [line.strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()]

    def generate_quiz_options(self, word: str) -> dict:
        prompt = f"""
        Create a multiple choice quiz question for the word '{word}'.
        Return in the following format:
        Question: What does the word '{word}' mean?
        Options:
        - option A
        - option B
        - option C
        - option D
        Correct Answer: option A

        Do not include any explanations or formatting like markdown.
        """
        response = self.giga.chat(prompt)
        content = response.choices[0].message.content.strip()

        # ---- Simple parsing ----
        question_match = re.search(r"Question:\s*(.*)", content)
        options_match = re.findall(r"- (.*)", content)
        correct_match = re.search(r"Correct Answer:\s*(.*)", content)

        return {
            "question": question_match.group(1).strip() if question_match else "",
            "options": [opt.strip() for opt in options_match],
            "correct_answer": correct_match.group(1).strip() if correct_match else "",
        }


# Фабричный метод для получения нужной модели
def get_linguistic_model(provider_name="gigachat") -> BaseLinguisticModel:
    if provider_name.lower() == "deepseek":
        return DeepSeekLinguisticModel()
    elif provider_name.lower() == "gigachat":
        return GigaChatModel()
    # Можно добавить другие провайдеры в будущем
    raise ValueError(f"Unknown provider: {provider_name}")
