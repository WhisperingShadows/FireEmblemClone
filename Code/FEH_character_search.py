from typing import Iterable
import difflib
from Code.FireEmblemCombatV2 import players_data
import logging

FORMAT = "%(asctime)-15s| %(message)s"
logging.basicConfig(format=FORMAT, level="DEBUG")


def remove_prefix(text: str, prefixes: Iterable) -> str:
    for prefix in prefixes:
        if text.startswith(prefix):
            return text[len(prefix):]
    return text  # or whatever


def remove_suffix(text: str, suffixes: Iterable) -> str:
    for suffix in suffixes:
        if text.endswith(suffix):
            return text[:-len(suffix)]
    return text  # or whatever


def dict_kv(dictionary: dict) -> list:
    return list(dictionary.keys()) + list(dictionary.values())


def invert_dict(dictionary: dict) -> dict:
    return {v: k for k, v in dictionary.items()}


def recursive_join(separator, *args) -> str:
    return str(separator).join([recursive_join(separator, *x) if type(x) is list else str(x) for x in args])


def flatten(input_list):
    if not input_list:
        return input_list
    if isinstance(input_list[0], list):
        return flatten(input_list[0]) + flatten(input_list[1:])
    return input_list[:1] + flatten(input_list[1:])


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    return seen_twice


def format_seq_to_cs_string(seq):
    """Takes a sequence as an input and returns a human-readable string of its values separated by commas
    (includes "and" before final item if sequence contains more than 1 item)"""
    string = ', '.join([str(i) for i in seq])
    if len(seq) > 1:
        position = string.rindex(", ")
        if len(seq) == 2:
            and_form = " and"
        else:
            and_form = ", and"
        return string[:position] + and_form + string[position + 1:]
    else:
        return string


prefix_dict = {
    "A": "Adult",  # prefix that identifies hero as an adult alt
    "POPULARITY": "Brave",  # prefix that identifies hero as a brave alt
    "DANCE": "Dancer",  # prefix that identifies hero as a dancer alt
    "PAIR": "Duo",  # prefix that identifies hero as a duo unit
    "LEGEND": "Legendary",  # prefix that identifies hero as a legendary hero
    "GOD": "Mythic",  # prefix that identifies hero as a mythic hero
    "BRIDE": "Bridal",  # prefix that identifies hero as a bridal alt
    "DARK": "Fallen",  # prefix that identifies hero as a fallen alt
    "HALLOWEEN": "Halloween",  # prefix that identifies hero as a halloween alt
    "SUMMER": "Summer",  # prefix that identifies hero as a summer alt
    "PICNIC": "Picnic",  # prefix that identifies hero as a picnic alt
    "SPRING": "Spring",  # prefix that identifies hero as a spring alt
    "VALENTINE": "Valentine",  # prefix that identifies hero as a valentine alt
    "WINTER": "Winter",  # prefix that identifies hero as a winter alt
    "ONSEN": "HotSprings",  # prefix that identifies hero as a Hot Springs alt
    "DREAM": "Adrift",  # prefix that identifies hero as an adrift alt
    "MIKATA": "Ally",  # prefix that identifies hero as a playable alt of a NPC
    "BON": "HoshidanSummer",  # prefix that identifies hero as a Hoshidan Summer alt
    "NEWYEAR": "NewYears",  # prefix that identifies hero as a New Years alt
    "KAKUSEI": "Awakening",  # prefix that identifies hero as an Awakening alt (only Anna so far)
    "ECHOES": "Echoes",  # prefix that identifies hero as an Echoes alt (only Catria so far)
    "BEFORE": "Young",  # prefix that identifies hero as a young alt
}

suffix_dict = {
    "M": "Male",
    "F": "Female",
}

extra_specs = [
    "Sword", "Lance", "Axe", "Red bow", "Blue bow", "Green bow", "Colorless bow", "Red Dagger", "Blue Dagger",
    "Green Dagger", "Colorless Dagger", "Red Tome", "Blue Tome", "Green Tome", "Colorless Tome", "Staff",
    "Red Breath", "Blue Breath", "Green Breath", "Colorless Breath", "Red Beast", "Blue Beast", "Green Beast",
    "Colorless Beast", "Infantry", "Armored", "Cavalry", "Flier"
]

extra_specs = {*flatten([i.split(" ") for i in extra_specs])}

name_set = players_data[2]
parted_name_set = flatten([i.split(" ") for i in name_set])


class DoesNotContainNameError(Exception):
    """Argument does not contain a valid character name"""

    def __init__(self, input_val="\b\b", intro="Could not find name in input: {0}"):
        self.message = intro.format(input_val)
        super().__init__(self.message)


class NoSuchNameError(Exception):
    """No such character exists with given name"""

    def __init__(self, input_val="\b\b", intro="No such character exists with given name: {0}"):
        self.message = intro.format(input_val)
        super().__init__(self.message)


class AltDoesNotExistError(Exception):
    """Character does not have alt of given specifications"""

    def __init__(self, alt="\b", character="\b\b", details="", intro="Could not find {0} {1}{2}"):
        if alt:
            alt += " alt for"
        else:
            alt = "non-alt version of"
        self.message = intro.format(alt, character, details)
        super().__init__(self.message)


class InvalidTokenError(Exception):
    """Token could not be found in token list. Token is not a known name, prefix, or suffix"""

    def __init__(self, token, intro="Token {0} is not a known name, prefix, or suffix"):
        self.message = intro.format(token)
        super().__init__(self.message)


class DuplicateTermsError(Exception):
    """Duplicates terms encountered in input"""

    def __init__(self, duplicates, intro="Duplicate terms encountered: {0}"):
        self.message = intro.format(', '.join([str(i) for i in duplicates]))
        super().__init__(self.message)


class MultipleNamesError(Exception):
    """Multiple names encountered in input. Only one name is accepted at a time."""

    def __init__(self, names, intro="Encountered more than one name in input: {0}"):
        self.message = intro.format(format_seq_to_cs_string(names))
        super().__init__(self.message)


token_filter = {"Ally", "Mythic"}


def filter_tokens(token_string, filter_set):
    # for filter_item in filter:
    #     if filter_item in token_list:
    #         token_list.replace(filter_item, "")
    token_list = token_string.split("_")
    return '_'.join([i for i in token_list if i not in filter_set])


def split_and_correct(name: str):
    corrected_name = ""
    corrected_prefixes = []
    corrected_suffixes = []
    for token in name.strip().split(" "):

        name_part = difflib.get_close_matches(token.title(), parted_name_set, 1, 0.7)
        corrected_suffix = difflib.get_close_matches(token.title(), [i.title() for i in dict_kv(suffix_dict)], 1, 0.7)
        extra_spec = difflib.get_close_matches(token.title(), extra_specs, 1, 0.7)
        corrected_prefix = difflib.get_close_matches(token.title(), [i.title() for i in dict_kv(prefix_dict)], 1, 0.8)

        token_types = [name_part, corrected_suffix, extra_spec, corrected_prefix]

        chosen = ""
        if sum(bool(i) for i in token_types):
            chosen = difflib.get_close_matches(token.title(), [*map(lambda L: L[0] if L else "-1", token_types)], 1)

        if (name_part and not chosen) or (name_part and chosen == name_part):
            corrected_name += name_part[0] + " "
            continue

        if (corrected_suffix and not chosen) or (corrected_suffix and chosen == corrected_suffix):
            corrected_suffix = corrected_suffix[0]
            # CHECK: Does scanning values work as fast as inverting and scanning keys?
            if corrected_suffix in suffix_dict.values():
                corrected_suffix = invert_dict(suffix_dict)[corrected_suffix]

            logging.debug("Suffix: %s", corrected_suffix)

            corrected_suffixes.append(corrected_suffix)
            logging.debug("Token {0} matches suffix {1}".format(token, corrected_suffix))
            continue

        if (extra_spec and not chosen) or (extra_spec and chosen == extra_spec):
            corrected_name += extra_spec[0] + " "
            continue

        if (corrected_prefix and not chosen) or (corrected_prefix and chosen == corrected_prefix):
            corrected_prefix = corrected_prefix[0]
            if corrected_prefix.upper() in prefix_dict.keys():
                logging.debug(
                    "Converting prefix {0} to {1}".format(corrected_prefix, prefix_dict[corrected_prefix.upper()]))
                corrected_prefix = prefix_dict[corrected_prefix.upper()]

            logging.debug("Prefix: %s", corrected_prefix)

            corrected_prefixes.append(corrected_prefix)
            logging.debug("Token {0} matches prefix {1}".format(token, corrected_prefix))
            continue

        # corrected_name = difflib.get_close_matches(token.title(), name_set, 1, 0.7)
        # if corrected_name:
        #     corrected_name = corrected_name[0]
        #     continue

        raise InvalidTokenError(token)

    if not corrected_name:
        raise DoesNotContainNameError(name)

    split_name = corrected_name.strip().split(" ")

    duplicates = list_duplicates(split_name)
    if duplicates:
        raise DuplicateTermsError(duplicates)

    if len([item for item in [*split_name, corrected_name] if item in name_set]) > 1:
        raise MultipleNamesError(split_name)

    corrected_prefixes = map(lambda string: filter_tokens(string, token_filter), corrected_prefixes)

    return corrected_name.strip(), ' '.join(corrected_prefixes).title(), ' '.join(corrected_suffixes).title()


words = [remove_prefix(i, ["PID_", "EID_"]) for i in players_data[0].keys()]


def get_character(name: str):
    name_token, prefixes, suffixes = split_and_correct(name)
    # print("From split&correct:", name_token, prefixes, suffixes)
    # name_token = name_token.replace(" ", "_")

    corrected_name = recursive_join(" ", [prefixes, name_token, suffixes]).strip()

    containing = [i for i in words if all(
        name_part in [j for j in i.split("_") if len(j) == len(name_part)] for name_part in name_token.split(" "))]
    # if not containing:
    #     print(name_token)
    #     print([word for word in words if "Knight" in word])
    #     print([filter_tokens(i, token_filter) for i in containing])
    # print("Filtered containing:", [filter_tokens(i, token_filter) for i in containing])

    # tokens = name.split(" ")

    if not containing:
        raise NoSuchNameError(name_token)

    logging.info("Contains name %s: %s", name_token, containing)

    logging.info("Corrected name: %s", corrected_name)

    output = \
        difflib.get_close_matches(corrected_name, [filter_tokens(i, token_filter) for i in containing], len(containing))

    if not output or (not prefixes and not suffixes and not name_token in containing and not any(
            [name_token.replace(" ", "_") + "_" + i in containing for i in suffix_dict])):
        # if len(containing) == 1:
        #     output = containing
        # else:

        output = [sorted(containing, key=lambda char: players_data[0]["PID_" + char]["id_num"])[0]]

        logging.warning("Selecting oldest version for %s" % name_token)

    logging.info("Output: %s" % output)

    # if len(output) == 1 and not prefixes and not corrected_name.split(" ")[-1] in keys_vals:
    #     logging.info("Only one option with given base name available, defaulting")

    if len(output) == 1 and all([i in output[0].split("_") for i in corrected_name.split(" ")]):
        logging.info("Only one option with given base name available, defaulting")

    elif output[0].split("_") != corrected_name.split(" "):
        details = ""
        keys_vals = list(suffix_dict.keys()) + list(suffix_dict.values())
        if len(output) == 2 and all((i.split("_")[-1] in keys_vals) for i in output):
            details = (". Gendered alts detected, please specify either male or female %s." % name_token)

        raise AltDoesNotExistError(recursive_join(" ", [prefixes, [suffix_dict[i] for i in suffixes]]).strip(),
                                   name_token, details)

    output = ["PID_" + option for option in output]

    logging.info("Close matches: %s \nMost probable: %s", output, output[0])

    return output


if __name__ == '__main__':
    version = input("Full scan mode (S) or individual testing (T)? >>> ")

    if version.lower() == "s":
        logging.disable(30)
        for name in name_set:
            try:
                get_character(name)
            except (DoesNotContainNameError, AltDoesNotExistError, InvalidTokenError, DuplicateTermsError,
                    MultipleNamesError, NoSuchNameError) as e:
                logging.error(e.message)

    elif version.lower() == "t":
        from time import sleep

        logging.disable(0)
        while True:
            try:
                sleep(0.1)
                get_character(input("Name: "))
            except (DoesNotContainNameError, AltDoesNotExistError, InvalidTokenError, DuplicateTermsError,
                    MultipleNamesError, NoSuchNameError) as e:
                logging.error(e.message)
        pass

    else:
        print("Invalid mode")
