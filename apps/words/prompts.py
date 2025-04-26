from abc import ABC

from apps.words.const import Prompts, ReturnFormatPrompt


class AbstractPromptBuilder(ABC): ...


class PromptBuilder(AbstractPromptBuilder):
    def get_word_definition(self, word: str) -> str:
        main_prompt = Prompts.WORD_DEFINITION.value.format(word=word)
        return_format = ReturnFormatPrompt.WORD_DEFINITION.value

        return main_prompt + return_format

    def get_word_examples(self, word: str, count: int) -> str:
        main_prompt = Prompts.WORD_EXAMPLES.value.format(word=word, count=count)
        return_format = ReturnFormatPrompt.WORD_EXAMPLES.value

        return main_prompt + return_format
