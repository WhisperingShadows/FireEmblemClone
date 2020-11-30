try:
    import sys

    sys.path.insert(0, r"C:\Users\admin\AppData\Local\Programs\Python\Python36\Lib\site-packages")
    import ujson as json

    print("Using UJSON")
except ImportError:
    import json

    print("Using JSON")

import os
from time import time


def merge_english_dicts(list_of_dicts):
    merged = {}
    for i_dict in list_of_dicts:
        # dicts are of the form {"key": key, "value": value}
        merged[i_dict["key"]] = i_dict["value"]
    return merged


from typing import List, Set, Dict, Optional
import queue, threading, os
import concurrent.futures

cores = 5


class ThreadedLoad:
    fileQueue = queue.Queue()
    lock = threading.Lock()
    data = {}
    count = 0

    def __init__(self, directory=""):
        self.directory = directory
        self.data = {}

    def __call__(self, fileList):
        return self.run(fileList)

    def run(self, fileList):
        return self.threadWorker(fileList)

    def Worker(self):
        fileName = self.fileQueue.get()

        with open((self.directory + "/" + fileName) if self.directory else fileName, "r",
                  encoding="utf-8") as json_data:
            tmp = json.load(json_data)

        with self.lock:
            self.data[fileName] = tmp
        #     self.count += 1
        #     print(fileQueue.queue)
        #     print(f"Task {self.count} done")
        #
        # print("Lock released")
        self.fileQueue.task_done()

    def threadWorker(self, filename_list: List[str]):
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            # print(f"Loading {len(filename_list)} files into queue")
            for filename in filename_list:
                self.fileQueue.put(filename)

                executor.submit(self.Worker)

            # print("Blocking until join")
            self.fileQueue.join()  # program waits for this process to be done.
            # print("Join done!")

        return self.data


def translate_jp_to_en_dict(input_dict, english_data, tag="id_tag", prefix="MSID_", old_prefix="SID_", is_skill=False):
    # Prefixes that begin with "M" refer to English entries (I think)

    # this was the result of like 4 days with no sleep, constantly coding, I have no idea how it works
    if is_skill:

        # initialize output to None
        output = None
        try:

            # if refined, is weapon, get base weapon and return with refine effect
            # not sure if this works for non atk/spd/def/res refines
            if input_dict["refined"]:
                output = str(translate_jp_to_en_dict(input_dict, english_data, tag="refine_base")) + "_" + (
                    input_dict["id_tag"].split("_")[-1])

            # if skill is not refined, try to translate it normally
            else:
                try:
                    output = translate_jp_to_en_dict(input_dict, english_data)

                # if skill cannot be translated
                except KeyError:

                    # been a while (4 months), but I believe this cannot be translated,
                    # the commented out line below returns the skill description (not name)
                    if input_dict["beast_effect_id"] is not None and input_dict["category"] == 8:
                        # output = translate_jp_to_en_dict(input_dict, english_data, prefix="MSID_H_")
                        return None

                    # this means it's a duo effect or something similar (beast effect?), doesn't catch all duos
                    if input_dict["beast_effect_id"] is None and input_dict["category"] == 8:
                        # duo skills don't have names, but they do have descriptions
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]

                        if input_dict["wep_equip"] == 0 and input_dict["skill_range"] == 0:
                            # Weird beast thing, not touching it
                            return None

                        # dprint("Duo Effect:", english_data[input_dict["id_tag"].replace("SID_", "MSID_H_")])
                        # print(skillsDict[skill].id_tag.replace("SID_", "MSID_H_"))
                        return None

                    if input_dict["id_tag"] == "SID_無し":
                        return "blank"

                    # category 7 refers to refined weapon skill effects, these normally have an R in them
                    # these also do not have a translation because they are simply an additional effect that is
                    # added onto the base weapon
                    # you could find the base weapon by iterating through all skill dicts and checking if they have
                    # an entry in their "refine_id" key and creating a dict that links all "refine_id" values to
                    # the value/entry in their "id_tag" key (so dicts would take form key = refine_id value,
                    # value = id_tag value)
                    if input_dict["category"] != 7:
                        output = translate_jp_to_en_dict(input_dict, english_data, prefix="MSID_H_")
                    pass

            return output

        except KeyError as e:
            print("Error:", e)
        pass
    else:
        return english_data[input_dict[tag].replace(old_prefix, prefix)]
    raise Exception("How did you get here")


def remove_digits(input_string: str) -> str:
    remove_digits_translation_table = str.maketrans('', '', "0123456789")
    output_string = input_string.translate(remove_digits_translation_table)
    return output_string


def get_jap_and_eng_name_dicts(list_of_dicts: List[Dict], output_category: str,
                               english_transl_data: Dict, get_short_names=True) \
        -> [dict, dict, Optional[Set]]:
    english_names = {}
    japanese_names = {}
    to_return = [english_names, japanese_names]

    if get_short_names:
        name_set = set()
        to_return.append(name_set)

    weapon_index_dict = {k: v for k, v in zip([i for i in range(24)], [
        "Sword", "Lance", "Axe", "Red bow", "Blue bow", "Green bow", "Colorless bow", "Red Dagger", "Blue Dagger",
        "Green Dagger", "Colorless Dagger", "Red Tome", "Blue Tome", "Green Tome", "Colorless Tome", "Staff",
        "Red Breath",
        "Blue Breath", "Green Breath", "Colorless Breath", "Red Beast", "Blue Beast", "Green Beast",
        "Colorless Beast"
    ])}

    # CHECK: Keep as "Flier" or change to "Flying"?
    move_index_dict = {0: "Infantry", 1: "Armored", 2: "Cavalry", 3: "Flier"}

    for i_dict in list_of_dicts:

        if i_dict["id_tag"] == "PID_無し" or i_dict["id_tag"] == "EID_無し":
            # maybe insert something that just uses these as blanks?
            continue

        if output_category == "player":

            # just the name (afaik)
            simple_name = translate_jp_to_en_dict(i_dict, english_transl_data,
                                                  prefix="MPID", old_prefix="PID")

            if get_short_names:
                name_set.add(simple_name)

            simple_name = simple_name.replace(" ", "_")

            # there's probably a reason for the digits at the end but I can't figure it out,
            # so I think it's safe to remove them
            # this finds all the unique unit identifiers, used for naming alts
            unit_identifiers = remove_digits(str(i_dict["roman"])).split("_")[1:]

            # suffix that identifies unit as male version (mainly used for protagonists)
            if "M" in unit_identifiers:
                suffix = "_M"
            # suffix that identifies unit as female version (mainly used for protagonists)
            elif "F" in unit_identifiers:
                suffix = "_F"
            # elif "A" in unit_identifiers:
            #     suffix = "_A"
            else:
                suffix = ""

            prefix_dict = {
                "A": "Adult_",  # prefix that identifies hero as an adult alt
                "POPULARITY": "Brave_",  # prefix that identifies hero as a brave alt
                "DANCE": "Dancer_",  # prefix that identifies hero as a dancer alt
                "PAIR": "Duo_",  # prefix that identifies hero as a duo unit
                "LEGEND": "Legendary_",  # prefix that identifies hero as a legendary hero
                "GOD": "Mythic_",  # prefix that identifies hero as a mythic hero
                "BRIDE": "Bridal_",  # prefix that identifies hero as a bridal alt
                "DARK": "Fallen_",  # prefix that identifies hero as a fallen alt
                "HALLOWEEN": "Halloween_",  # prefix that identifies hero as a halloween alt
                "SUMMER": "Summer_",  # prefix that identifies hero as a summer alt
                "PICNIC": "Picnic_",  # prefix that identifies hero as a picnic alt
                "SPRING": "Spring_",  # prefix that identifies hero as a spring alt
                "VALENTINE": "Valentine_",  # prefix that identifies hero as a valentine alt
                "WINTER": "Winter_",  # prefix that identifies hero as a winter alt
                "ONSEN": "HotSprings_",  # prefix that identifies hero as a Hot Springs alt
                "DREAM": "Adrift_",  # prefix that identifies hero as an adrift alt
                "MIKATA": "Ally_",  # prefix that identifies hero as a playable alt of a NPC
                "BON": "HoshidanSummer_",  # prefix that identifies hero as a Hoshidan Summer alt
                "NEWYEAR": "NewYears_",  # prefix that identifies hero as a New Years alt
                "KAKUSEI": "Awakening_",  # prefix that identifies hero as an Awakening alt (only Anna so far)
                "ECHOES": "Echoes_",  # prefix that identifies hero as an Echoes alt (only Catria so far)
                "BEFORE": "Young_",  # prefix that identifies hero as a young alt
            }

            prefix = ""
            # combines all identifers into (hopefully) unique identifier prefix for unit
            for identifier in prefix_dict:
                if identifier in unit_identifiers:
                    prefix += prefix_dict[identifier]

            # translated name with identifier prefixes and M/F suffix
            translated_name = ("PID_" + prefix + simple_name + suffix).strip()

            if translated_name not in english_names:
                english_names[translated_name] = i_dict
            else:
                # This is where we go if the identifier combo + name for a unit isn't unique
                # this is not a fun place to be

                # If weapon-type and move-type doesn't make these units unique then I give up

                # if output_as_class:
                #     # creates new entry that includes id_num in key for old entry
                #     my_dict["PID_" + str(my_dict[translated_name].id_num).replace(" ", "")
                #             + "_" + str(translated_name).replace("PID_", "")] = my_dict[translated_name]
                #
                #     # creates new entry that includes id_num in key for duplicate entry
                #     my_dict["PID_" + str(idict["id_num"]).replace(" ", "") + "_" +
                #             str(translated_name).replace("PID_", "")] = output_class.from_dict(input_dict=idict)
                # else:
                #     # creates new entry that includes id_num in key for old entry
                #     my_dict["PID_" + str(my_dict[translated_name]["id_num"])
                #             .replace(" ", "") + "_" + str(translated_name).replace("PID_", "")] \
                #         = my_dict[translated_name]
                #
                #     # creates new entry that includes id_num in key for duplicate entry
                #     my_dict["PID_" + str(idict["id_num"]).replace(" ", "") + "_" +
                #             str(translated_name).replace("PID_", "")] = idict

                # extracts gender from face file
                def get_gender(dictionary: dict):
                    gender = [i for i in str(dictionary["face_name"]).split("_") if i.upper() in ["M", "F"]]
                    # print(gender)

                    if len(gender) == 0:
                        return ""
                    elif len(gender) == 1:
                        return gender[0].strip()
                    else:
                        raise ValueError(
                            "Face_name of unit {0} contains more than one gender".format(i_dict["id_num"]))

                # changes up the name and its duplicate so that they aren't matching anymore
                def deduplicate(name: str, name_dict, all_names_dict=english_names) -> (str, str):

                    # creates new name entry that includes weapon and move type for old entry
                    old_entry = str(
                        "PID_" +
                        str(weapon_index_dict[all_names_dict[name]
                        ["weapon_type"]]).replace(" ", "_") +  # weapon type
                        "_" +
                        str(move_index_dict[all_names_dict[name]["move_type"]]) +  # move type
                        "_" +
                        str(name).replace("PID_", ""))  # name with identifiers

                    # creates new name entry that includes weapon and move type for name that
                    # caused duplicate error (pesky little thing)
                    duplicate_entry = str(
                        "PID_" +
                        str(weapon_index_dict[name_dict["weapon_type"]]).replace(" ", "_") +  # weapon type
                        "_" +
                        str(move_index_dict[name_dict["move_type"]]) +  # move type
                        "_" +
                        str(name).replace("PID_", ""))  # name with identifiers

                    # if the weapon and move type addition didn't solve the duplicate names,
                    # try adding gender to the name too
                    # this is not the same as the M/F suffix from earlier, since those are mostly
                    # reserved for main FE series protagonists (which always have both a male
                    # and a female version
                    if old_entry == duplicate_entry:
                        old_entry += "_" + get_gender(all_names_dict[name])
                        duplicate_entry += "_" + get_gender(name_dict)

                    return old_entry, duplicate_entry

                old_entry, duplicate_entry = deduplicate(translated_name, i_dict)

                # adds new entries to the dictionary
                english_names[old_entry] = english_names[translated_name]
                english_names[duplicate_entry] = i_dict

                # deletes old entry without id_num in name
                del english_names[translated_name]

        if output_category == "enemy":
            # I may be wrong, but I think I should add the same differentiating code as for player
            # names into here too

            translated_name = translate_jp_to_en_dict(i_dict, english_transl_data,
                                                      prefix="MEID", old_prefix="EID")

            english_names[translated_name] = i_dict

        if output_category == "skill":
            translate_output = translate_jp_to_en_dict(i_dict, english_data=english_transl_data,
                                                       is_skill=True)
            if translate_output is not None:
                english_names[translate_output] = i_dict

        japanese_names[i_dict["id_tag"]] = i_dict

    return to_return


def load_files(get_english_data=True, get_skills=True, get_characters=True, get_weapons=True,
               get_growth=True, get_move=True, get_stage_encount=True, get_terrain=True,
               check_for_update=False, get_simple_names=False):
    hold_path = os.path.dirname(os.path.dirname(__file__))

    english_data = {}

    if get_english_data:
        os.chdir(os.path.join(hold_path, "HertzDevil_JSON_assets/USEN/Message/Data"))

        english_data = ThreadedLoad().run(os.listdir())

        my_list = []
        for english_data_entry in english_data:
            my_list.extend(english_data[english_data_entry])

        english_data = merge_english_dicts(my_list)

    def process_data(data_loc, output, output_type):
        try:
            single_file = False
            output.update(ThreadedLoad(data_loc).run(os.listdir(data_loc)))
        except NotADirectoryError:
            single_file = True
            with open(data_loc, "r", encoding="utf-8") as json_data:
                output = json.load(json_data)

        # if the data is of a special type (like skills, characters, weapons),
        # then get translated versions
        if output_type:
            if not single_file:
                # dictionary to list of dictionary's values
                # combines data from multiple files into one large list of dicts
                dict_values_list = []
                for key in output:
                    dict_values_list.extend(output[key])
            else:
                dict_values_list = output

            output = get_jap_and_eng_name_dicts(dict_values_list, output_type,
                                                english_data, get_simple_names)

        return output

    os.chdir(hold_path)
    os.chdir(os.path.abspath("HertzDevil_JSON_assets//Common/SRPG"))

    skills = {}
    players = {}
    enemies = {}
    weapons = {}
    growth = {}
    move = {}
    stage_encount = {}
    terrain = {}

    if get_skills:
        skills = process_data("Skill", skills, "skill")

    if get_characters:
        players = process_data("Person", players, "player")

        # ===========================================

        enemies = process_data("Enemy", enemies, "enemy")

    if get_weapons:
        weapons = process_data("Weapon.json", weapons, "weapons")

    if get_growth:
        growth = process_data("Grow.json", growth, None)

    if get_move:
        move = process_data("Move.json", move, None)

    if get_stage_encount:
        stage_encount = process_data("StageEncount.json", stage_encount, None)

    if get_terrain:
        terrain = process_data("Terrain.json", terrain, None)

    os.chdir(hold_path)
    return skills, players, enemies, weapons, english_data, growth, move, stage_encount, terrain


def test():
    from timeit import timeit

    number = 3

    try:
        print("Using json")
        import json as json
        print(timeit("load_files()", globals={"load_files": load_files}, number=number))
    except ImportError:
        pass

    try:
        print("Using rapidjson")
        import rapidjson as json
        print(timeit("load_files()", globals={"load_files": load_files}, number=number))
    except ImportError:
        pass

    try:
        print("Using ujson")
        import ujson as json
        print(timeit("load_files()", globals={"load_files": load_files}, number=number))
    except ImportError:
        pass

    try:
        print("Using orjson")
        import orjson as json
        print(timeit("load_files()", globals={"load_files": load_files}, number=number))
    except ImportError:
        pass


if __name__ == '__main__':
    start = time()
    skills, players, enemies, weapons, english_data, growth, move, stage_encount, terrain = load_files()
    print("Time elapsed:", time() - start)

    # print(players[0]["PID_Marth"])

    pass
