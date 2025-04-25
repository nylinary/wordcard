from enum import Enum


class ReturnFormat(dict, Enum):
    WORD_DEFINITION = {"definition": "", "part_of_speech": ""}


class ReturnFormatPrompt(str, Enum):
    WORD_DEFINITION = f"""Return answer in JSON format. Here is format: {ReturnFormat.WORD_DEFINITION.value}."""


class Prompts(str, Enum):
    WORD_DEFINITION = """
        You are an assistant helping English learners.
        Define the word or phrase: '{word}' in clear and simple English.
        Return plain text only. Do not include any explanations, examples, markdown, numbering, or titles.
        Max length of the answer is 512 symbols.
        """

    WORD_EXAMPLES = """
        You are an assistant helping English learners.
        Return exactly 2 example sentences showing how the word or phrase '{word}' is used.
        Do not explain them. Do not include markdown or extra text.
        Just return the two sentences, each on its own line.
        Example format:
        I need to get over my fear of heights before I can go skydiving.
        She's trying to get over her ex-boyfriend.
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
