import json
import os
# from pprint import pprint
from time import time


def load_files_kag_calc_ver(get_assists=True, get_driveskills=True, get_heroes=True, get_passives=True,
                            get_specials=True, get_weapons=True, get_blessings=True, get_refinements=True,
                            get_support_bonus=True):
    # print("Starting")
    start = time()
    os.chdir(r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\data")
    # print(os.listdir())

    assists = {}
    driveskills = {}
    heroes = {}
    passives = {}
    specials = {}
    weapons = {}

    blessings = {}
    refinements = {}
    support_bonus = {}

    def json_file_to_dict(file_location, dict):
        with open(file_location, "r", encoding="utf-8") as json_data:
            dict[file_location.replace(".json", "")] = json.load(json_data)

    if get_blessings:
        json_file_to_dict("blessings.json", blessings)
    if get_refinements:
        json_file_to_dict("refinements.json", refinements)
    if get_support_bonus:
        json_file_to_dict("support-bonus.json", support_bonus)

    if get_assists:
        for file in os.listdir("assists"):
            # print(file)
            with open(r"assists/" + file, "r", encoding="utf-8") as json_data:
                assists[file.replace(".json", "")] = json.load(json_data)
                del assists[file.replace(".json", "")]["link"]

    if get_driveskills:
        for file in os.listdir("driveskills"):
            # print(file)
            with open(r"driveskills/" + file, "r", encoding="utf-8") as json_data:
                driveskills[file.replace(".json", "")] = json.load(json_data)

    if get_heroes:
        for file in os.listdir("heroes"):
            # print(file)
            with open(r"heroes/" + file, "r", encoding="utf-8") as json_data:
                heroes[file.replace(".json", "")] = json.load(json_data)
                del heroes[file.replace(".json", "")]["link"]

    if get_passives:
        for folder in os.listdir("passives"):
            passives[folder] = {}
            for file in os.listdir("passives/" + folder):
                # print(file)
                with open(r"passives/" + folder + "/" + file, "r", encoding="utf-8") as json_data:
                    passives[folder][file.replace(".json", "")] = json.load(json_data)
                    try:
                        del passives[folder][file.replace(".json", "")]["link"]
                    except KeyError:
                        pass
                        # if e.args[0] == 'link':
                        #     print("Link not found, skipping")
                        # else:
                        #     raise KeyError(e)
    if get_specials:
        for file in os.listdir("specials"):
            # print(file)
            with open(r"specials/" + file, "r", encoding="utf-8") as json_data:
                specials[file.replace(".json", "")] = json.load(json_data)
                del specials[file.replace(".json", "")]["link"]

    if get_weapons:
        for file in os.listdir("weapons"):
            # print(file)
            with open(r"weapons/" + file, "r", encoding="utf-8") as json_data:
                weapons[file.replace(".json", "")] = json.load(json_data)
                del weapons[file.replace(".json", "")]["link"]

    stop = time()
    print("Time elapsed:", stop - start, "secs")
    return assists, driveskills, heroes, passives, specials, weapons, blessings, refinements, support_bonus


class Weapon:
    def __init__(self, **kwargs):
        print(kwargs)
        if "input_dict" in kwargs:
            kwargs = kwargs['input_dict']
        for key in [_ for _ in kwargs]:
            setattr(self, key, kwargs[key])

    @classmethod
    def from_dict(cls, input_dict):
        return cls(input_dict=input_dict)


if __name__ == "__main__":
    assists, driveskills, heroes, passives, specials, weapons, blessings, refinements, support_bonus = load_files_kag_calc_ver()

    # for weapon in weapons:
    #     print(weapons[weapon])
    #     print(len(weapons[weapon]))
    #     classWeapon = Weapon.from_dict(weapons[weapon])
    #     print(classWeapon)
    #     print(classWeapon.name)
    # classWeapon = Weapon(name = "My name")
    # print(classWeapon)
    # print(classWeapon.name)

    # from pprint import pprint

    # for key in weapons:
    #     pprint(key)
    #     for key2 in weapons[key]:
    #         print(key2)

    # for folder in passives:
    #     for skill in passives[folder]:
    #         pprint(passives[folder][skill])
