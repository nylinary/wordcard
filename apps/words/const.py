from enum import Enum


class ReturnFormat(Enum):
    WORD_DEFINITION = {"definition": "", "part_of_speech": ""}
    WORD_EXAMPLES = ["sentence_1", "sentence_2"]


class ReturnFormatPrompt(str, Enum):
    WORD_DEFINITION = f"""Return answer in JSON format. Here is format: {ReturnFormat.WORD_DEFINITION.value}."""
    WORD_EXAMPLES = f"""
        Return answer in JSON format as list of sentences. Here is format: {ReturnFormat.WORD_EXAMPLES.value}."""


class Prompts(str, Enum):
    WORD_DEFINITION = """
        You are an assistant helping English learners.
        Define the word or phrase: '{word}' in clear and simple English.
        Return plain text only. Do not include any explanations, examples, markdown, numbering, or titles.
        Max length of the answer is 512 symbols.
        Answer must not be too short. It must give a english learner an understanding of word meaning.
        """
    WORD_EXAMPLES = """
        You are an assistant helping English learners.
        Return exactly {count} example sentences showing how the word or phrase '{word}' is used.
        Do not explain them. Do not include markdown or extra text. Sentences should be not too short.
        They must give user great example to understand usage of word or phrase in different contexts.
        The sentences MUST include the given word or phrase.
        """
    WORD_QUIZ = """
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
