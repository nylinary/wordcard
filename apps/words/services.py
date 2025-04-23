import abc
import re

from django.conf import settings
from gigachat import GigaChat
from openai import OpenAI

from apps.words.const import Prompts


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
        prompt = Prompts.WORD_DEFINITION.value.format(word=word)
        completion = self.client.chat.completions.create(
            extra_body={}, model="deepseek/deepseek-r1:free", messages=[{"role": "user", "content": prompt}]
        )
        return {"word": word, "part_of_speech": "", "definition": completion.choices[0].message.content}

    def get_word_examples(self, word: str) -> list:
        prompt = Prompts.WORD_EXAMPLES.value.format(word=word)
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
        prompt = Prompts.WORD_DEFINITION.value.format(word=word)
        response = self.giga.chat(prompt)
        return {"word": word, "part_of_speech": "", "definition": response.choices[0].message.content.strip()}

    def get_word_examples(self, word: str) -> list:
        prompt = Prompts.WORD_EXAMPLES.value.format(word=word)
        response = self.giga.chat(prompt)
        return [line.strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()]

    def generate_quiz_options(self, word: str) -> dict:
        prompt = Prompts.WORD_QUIZ.value.format(word=word)
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
