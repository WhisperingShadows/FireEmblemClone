# TODO: Create autocorrect class that is called on all text input (override input method)
# TODO: Add register function to register new autocorrect categories (ex. names, prefixes, suffixes, commands)

# CHECK: Do I really need a singleton class? Couldn't I just use only class methods and prevent instances?

import difflib
try:
    from utility_functions import flatten
except ImportError:
    from Tools.utility_functions import flatten


# import string

# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


class AutoCorrect:
    # dictionary of valid autocorrect corrections
    correction_dict = dict()
    # stores reference to builtin input method, for faster lookup (roughly 3x faster)
    input_reference = input
    # similarity cutoff for difflib's get_close_matches function
    cutoff = 0.6

    @classmethod
    def register(cls, category, words):
        """
        Registers new autocorrection categories and words.

        :param category:
        :param words:
        :return:
        """
        cls.correction_dict[category] = words

    @classmethod
    def input(cls, prompt=''):
        """
        Input method used by autocorrect class. Takes in input using builtin input method and returns corrected
        input. Supports input prompt.

        :param prompt:
        :return:
        """
        text_in = cls.input_reference(prompt)
        corrected_text = cls.auto_correct(text_in)
        return corrected_text

    @classmethod
    def auto_correct(cls, input_string):
        """
        Takes in argument input_string, splits by spaces to create word tokens, and replaces each token with
        closest match in the class' correction_dict. Returns string of tokens joined by spaces (preserves order).

        :param input_string: string
        :return: string
        """

        # input_string = cls.filter_input(input_string)

        possible_corrections = dict()
        output = []

        for token in input_string.strip().split(" "):
            # print(token)
            for category, words in cls.correction_dict.items():
                possible_corrections[category] = difflib.get_close_matches(token.title(), words, 1, cls.cutoff)

            # print("Possible:", flatten([i for i in possible_corrections.values()]))

            corrected = difflib.get_close_matches(token.title(), flatten([i for i in possible_corrections.values()]), 1,
                                                  cls.cutoff)
            if corrected:
                output.append(corrected[0])

        return ' '.join(output)

    @classmethod
    def override_input(cls):
        """
        Overrides builtin input method with class input method.

        :return:
        """
        globals()["input"] = cls.input

    @classmethod
    def restore_input(cls):
        """
        Restores builtin input method.

        :return:
        """
        del globals()["input"]

    @classmethod
    def switch_input(cls):
        """
        Switches between builtin input method and class input method, depending on which is currently
        being used.

        :return:
        """
        try:
            assert globals()["input"]
            cls.restore_input()
        except KeyError:
            cls.override_input()
