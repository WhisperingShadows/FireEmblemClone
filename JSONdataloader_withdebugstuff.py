import json
import os
from pprint import pprint
from time import time
from dprint import dprint

DEBUG = True


class Skill:

    def __init__(self, **kwargs):
        # print(kwargs)
        if "input_dict" in kwargs:
            kwargs = kwargs['input_dict']
        for key in [_ for _ in kwargs]:
            # print(key, kwargs[key])
            setattr(self, key, kwargs[key])

    @classmethod
    def from_dict(cls, input_dict):
        return cls(input_dict=input_dict)

    #
    # # Full internal string identifier of the skill e.g. SID_ジークリンデ_共 for Sieglinde
    # self.id_tag = id_tag
    # # Internal string identifier of the unrefined version of the weapon e.g. SID_ジークリンデ
    # self.refine_base = refine_base
    # #  Internal string identifier of the skill name resource e.g. MSID_ジークリンデ
    # self.name_id = name_id
    # # Internal string identifier of the skill description resource, e.g. MSID_H_ジークリンデ改
    # self.desc_id = desc_id
    # # Internal string identifier of the skill that gives rise to the refined skill effect, e.g. SID_強化共有R
    # self.refine_id = refine_id
    # # Internal string identifier of the skill that activates while the unit is transformed into
    # # a beast, e.g. SID_化身効果・奥義強化
    # self.beast_effect_id = beast_effect_id
    # # Internal string identifiers of skills required to learn the current skill.
    # self.prerequisites[2] = prerequisites[2]
    # # Internal string identifier of the canonical upgrade of the current skill. It is defined if and only if
    # # promotion_rarity is not zero.
    # self.next_skill = next_skill
    # # Filenames of the sprites used by the weapon, in this order: bow, weapon / arrow, map animation,
    # # AoE Special map animation.
    # self.sprites[4] = sprites[4]
    #
    # # Permanent stat bonuses of the skill. For weapons this does not include might.
    # self.stats = stats
    #
    # # A set of extra parameters that are used only for skill effects common to weapon classes for which
    # # weapon_class_definition::is_staff, is_dagger, is_breath, or is_beast is true:
    # #   - is_staff: If class_params.hp = 1, calculates damage from staff like other weapons.;
    # #     If class_params.hp = 2, foe cannot counterattack.
    # #   - is_dagger: After combat, if unit attacked, inflicts stat+class_params on target and foes within
    # #     class_params.hp spaces of target through their next actions.
    # #   - is_breath: If class_params.hp = 1, and if target_mov foe uses target_wep, calculates damage
    # #     using the lower of foe's Def or Res.
    # #   - is_beast: If class_params.hp = 1, at start of turn, if unit is adjacent to only beast or
    # #     dragon allies or if unit is not adjacent to any ally, unit transforms (otherwise, unit reverts);
    # #     if unit transforms, grants stat+class_params.
    # self.class_params = class_params
    #
    # # Various skill parameters packed into a stat tuple. These do not necessarily represent stat values.
    # # Their meanings depend on the skill abilities.
    # self.skill_params = skill_params
    #
    # # Stat bonuses of the skill's refinement, as shown on the weapon description.
    # self.refine_stats = refine_stats
    # # A unique increasing index for every skill, added to 0x10000000 for refined weapons.
    # self.id_num = id_num
    # # The internal sort value used in places such as the skill inheritance menu to order skills within
    # # the same category according to their skill families.
    # self.sort_id = sort_id
    # # The icon index of the skill, referring to the files UI/Skill_Passive*.png.
    # self.icon_id = icon_id
    # # A bitmask indexed by weapon_index, with bits set for weapon classes that can equip the current skill.
    # self.wep_equip = wep_equip
    # # A bitmask indexed by move_index, with bits set for movement classes that can equip the current skill.
    # self.mov_equip = mov_equip
    # #  SP required to learn the given skill.
    # self.sp_cost = sp_cost
    # # Category of the skill.
    # # 0	0xBC	Weapon
    # # 1	0xBD	Assist
    # # 2	0xBE	Special
    # # 3	0xBF	Passive A
    # # 4	0xB8	Passive B
    # # 5	0xB9	Passive C
    # # 6	0xBA	Sacred Seal
    # # 7	0xBB	Refined weapon skill effect
    # # 8	0xB4	Beast transformation effect
    # self.category = category
    #
    # # The element type for tome weapon skills.
    # self.tome_class = tome_class
    # # True if the skill cannot be inherited.
    # self.exclusive = exclusive
    # # True if the skill can only be equipped by enemies.
    # self.enemy_only = enemy_only
    # # Range of the skill for weapons and Assists, 0 for other skills.
    # self.range = range
    # # Might for weapon skills, including bonuses that come from refinements, 0 for other skills.
    # self.might = might
    # # Cooldown count of the skill. The total cooldown count of a unit is the sum of cooldown_count
    # # for all equipped skills. Skills that accelerate Special trigger have a negative value.
    # self.cooldown_count = cooldown_count
    # # True if the skill grants Special cooldown count-1 to the unit after this Assist is used.
    # self.assist_cd = assist_cd
    # # True if the skill is a healing Assist skill.
    # self.healing = healing
    # #  Range of the skill effect that comes with the given skill, e.g. 1 for Hone skills and
    # #  weapons that give equivalent skill effects.
    # self.skill_range = skill_range
    # # A value that roughly corresponds to the SP cost of the skill. Might have been used for Arena matches.
    # self.score = score
    # # 2 for a few low-tier Specials and staff weapons / Assists, 0 for highest-tier skills,
    # # and 1 for everything else. Used by derived maps to determine how far skills are allowed to promote.
    # self.promotion_tier = promotion_tier
    # # If non-zero, this skill would be promoted on derived maps if the unit's rarity is greater than or
    # # equal to this value.
    # self.promotion_rarity = promotion_rarity
    # # True if the skill is a refined weapon.
    # self.refined = refined
    # # Internal sort value for refined weapons: 1 and 2 for skills, 101 – 104 for Atk/Spd/Def/Res refinements,
    # # 0 otherwise.
    # self.refine_sort_id = refine_sort_id
    # # A bitmask indexed by weapon_index, representing weapon class effectivenesses this skill grants.
    # # Only meaningful on weapon skills.
    # self.wep_effective = wep_effective
    # # A bitmask indexed by move_index, representing movement class effectivenesses this skill grants.
    # # Only meaningful on weapon skills.
    # self.mov_effective = mov_effective
    # # A bitmask indexed by weapon_index, representing weapon class effectivenesses this skill protects from.
    # # Used by Breath of Blight.
    # self.wep_shield = wep_shield
    # # A bitmask indexed by move_index, representing movement class effectivenesses this skill protects from.
    # self.mov_shield = mov_shield
    # # A bitmask indexed by weapon_index, representing weapon class weaknesses this skill grants.
    # # Used by Loptous.
    # self.wep_weakness = wep_weakness
    # # A bitmask indexed by move_index, representing movement class weaknesses this skill grants.
    # # Currently unused.
    # self.mov_weakness = mov_weakness
    # # A bitmask indexed by weapon_index, representing weapon classes that receive damage from this
    # # skill calculated using the lower of Def or Res. Used by breaths. Only meaningful on weapon skills.
    # self.wep_adaptive = wep_adaptive
    # # A bitmask indexed by move_index, representing movement classes that receive damage from this
    # # skill calculated using the lower of Def or Res. Currently unused. Only meaningful on weapon skills.
    # self.mov_adaptive = mov_adaptive
    # # An index into the string table in Common/SRPG/SkillTiming.bin indicating the moment where the skill triggers.
    # self.timing_id = timing_id
    # # An index into the string table in Common/SRPG/SkillAbility.bin indicating the skill effect type.
    # # A skill can only contain one skill effect (refined weapons have an extra skill effect if
    # # refine_id is non-null).
    # self.ability_id = ability_id
    # # An index into the string table in Common/SRPG/SkillTiming.bin indicating the skill's activation restriction.
    # self.limit1_id = limit1_id
    # # Restriction-dependent parameters.
    # self.limit1_params[2] = limit1_params[2]
    # # An additional activation restriction on the given skill. Both must be satisfied for the skill to activate.
    # self.limit2_id = limit2_id
    # self.limit2_params[2] = limit2_params[2]
    # # A bitmask indexed by weapon_index, representing the target's weapon classes required for the
    # # skill's effect to activate. If zero, works on all weapon classes.
    # self.target_wep = target_wep
    # # A bitmask indexed by move_index, representing the target's movement classes required for the
    # # skill's effect to activate. If zero, works on all movement classes.
    # self.target_mov = target_mov
    # # Like next_skill, except that this field is null for weapons, Spur Atk 2 does not point to Spur Atk 3,
    # # and similarly for the three other Spur passives.
    # # (Death Blow 3 pointed to Death Blow 4 even before the CYL2 update.)
    # self.passive_next = passive_next
    #
    #
    # # A POSIX timestamp relative to the skill's release date; half a month into the future for skills
    # # released before Version 2.0.0, 1 month into the future for skills released since Version 2.0.0.
    # # This skill may be equipped by random units if timestamp is -1 or the current time is past timestamp.
    # self.timestamp = timestamp
    # # Indicates whether random units can equip this skill. This affects Training Tower and Allegiance Battles.
    # # It has 3 possible values:
    # #   - 0: This skill may not be equipped on random units.
    # #   - 10: This skill may be equipped on random units.
    # #   - 20: Purpose unknown. Same effect as 10. Used by basic non-staff weapons
    # #     (e.g. Iron Sword, Flametongue+, Adult (Cavalry)) and basic staff Assists.
    # self.random_allowed = random_allowed
    # # If non-zero, represent the lowest and highest levels respectively that allow random units
    # # to equip the given skill.
    # self.min_lv = min_lv
    # self.max_lv = max_lv
    # # If true, this skill may be considered by the 10th Stratum of the Training Tower for the
    # # random skill pool if it is equipped by the corresponding unit from the base map.
    # self.tt_inherit_base = tt_inherit_base
    # # Controls how random units may equip this skill. It has 3 possible values: (see #Random skills for details)
    # #   - 0: This skill may not be equipped on random units.
    # #   - 1: This skill may be equipped by any random unit.
    # #   - 2: This skill may be equipped by random units that own the skill.
    # self.random_mode = random_mode
    #
    #
    # # Unknown usage
    # # self.range_shape = range_shape
    # # self.id_tag2 = id_tag2
    # # self.next_seal = next_seal
    # # self.prev_seal = prev_seal
    # # self.ss_coin = ss_coin
    # # self.ss_badge_type = ss_badge_type
    # # self.ss_badge = ss_badge
    # # self.ss_great_badge = ss_great_badge


class Character:

    def __init__(self, **kwargs):
        # print(kwargs)
        if "input_dict" in kwargs:
            kwargs = kwargs['input_dict']
        for key in [_ for _ in kwargs]:
            setattr(self, key, kwargs[key])

    @classmethod
    def from_dict(cls, input_dict):
        return cls(input_dict=input_dict)


class Player(Character):
    pass


class Enemy(Character):
    pass


class Weapon:

    def __init__(self, **kwargs):
        # print(kwargs)
        if "input_dict" in kwargs:
            kwargs = kwargs['input_dict']
        for key in [_ for _ in kwargs]:
            setattr(self, key, kwargs[key])

    @classmethod
    def from_dict(cls, input_dict):
        return cls(input_dict=input_dict)


# to use, put two lines below into if get_english_data
# from functools import reduce
# english_data = reduce(rec_merge, [dict(i = english_data[i]) for i in english_data])["i"]

from collections import MutableMapping


def rec_merge(d1, d2):
    """
    Update two dicts of dicts recursively,
    if either mapping has leaves that are non-dicts,
    the second's leaf overwrites the first's.
    """
    for k, v in d1.items():  # in Python 2, use .iteritems()!
        if k in d2:
            # this next check is the only difference!
            if all(isinstance(e, MutableMapping) for e in (v, d2[k])):
                d2[k] = rec_merge(v, d2[k])
            # we could further check types and merge as appropriate here.
    d3 = d1.copy()
    d3.update(d2)
    return d3


def my_merger(list_of_dicts):
    my_dict = {}
    for idict in list_of_dicts:
        my_dict[idict["key"]] = idict["value"]
    return my_dict


def load_files(get_english_data=True, get_skills=True, get_characters=True, get_weapons=True):
    # print("Starting")
    start = time()

    english_data = {}

    if get_english_data:
        os.chdir(r"/Resources/data/assets/USEN/Message/Data")

        total = int()
        for file in os.listdir():
            dprint("Processing:", file)
            with open(file, "r", encoding="utf-8") as json_data:
                english_data[file.replace(".json", "")] = json.load(json_data)
                dprint(len(english_data[file.replace(".json", "")]))
                total += len(english_data[file.replace(".json", "")])
        dprint("Total:", total)

        myList = []
        for key in english_data:
            myList.extend(english_data[key])

        dprint("mylist length:", len(myList))

        dprint(len(english_data))

        # wicked cool list comprehension but it's about 1.6x slower than using my_merger()
        # new_var = {var[0]: var[1] for var in [(eng_dict["key"], eng_dict["value"]) for eng_dict in english_data]}

        english_data = my_merger(myList)

    def translate_jp_to_en(input_dict, tag="id_tag", prefix="MSID_", old_prefix="SID_", is_skill=False):

        if is_skill:
            output = None
            try:
                if input_dict["refined"]:
                    # removes refinement suffixes like _ATK or _DEF
                    # skillsDict[skill].id_tag.split("_")[0:-1]
                    # skillsDict[skill].roman_name = english_data[skillsDict[skill].refine_base.replace("SID_", "MSID_")]
                    output = translate_jp_to_en(input_dict, tag="refine_base")
                    print("Output1 here:", output)
                else:
                    try:
                        # x = repr((skill, ":", english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]))
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]
                        output = translate_jp_to_en(input_dict)
                        print("Output2 here:", output)

                    except KeyError as e:
                        # print(i)
                        # print("Using MSID_H instead")
                        # print(skillsDict[i].id_tag.replace("SID_", "MSID_H_"))
                        dprint("\n")

                        # dprint("Beast effect id:", input_dict["beast_effect_id"], "Category:", input_dict["category"])
                        # this means it's a duo effect or something similar (beast effect?)
                        if input_dict["beast_effect_id"] == None and input_dict["category"] == 8:
                            # duo skills don't have names, but they do have descriptions
                            # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]

                            if input_dict["wep_equip"] == 0 and input_dict["skill_range"] == 0:
                                # print("Beast thing, not touching it")
                                return None

                            dprint("Duo Effect:", english_data[input_dict["id_tag"].replace("SID_", "MSID_H_")])
                            # print(skillsDict[skill].id_tag.replace("SID_", "MSID_H_"))

                            # if hex(skillsDict[skills].wep_equip) & hex(weapon_index)

                            return None

                        if input_dict["id_tag"] == "SID_無し":
                            return "blank"

                        # y = repr((skill, ":", english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_H_")]))
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_H_")]
                        # output = translate_jp_to_en(input_dict, prefix="MSID_H_")
                        if output is not None:
                            print("Output:", output)
                        dprint("\n")
                        pass

                # anotherDict[output] = input_dict.id_tag
                return output
                # print(cur_skill.id_tag, ":", cur_skill.roman_name)

            except KeyError as e:
                print("Error:", e)
            pass
        else:
            return english_data[input_dict[tag].replace(old_prefix, prefix)]
        raise Exception("How did you get here?")

    def my_merger2(list_of_dicts, output_class):
        my_dict = {}
        my_dict2 = {}
        for idict in list_of_dicts:

            if idict["id_tag"] == "PID_無し" or idict["id_tag"] == "EID_無し":
                continue

            if output_class == Player:
                print(translate_jp_to_en(idict, prefix="MPID_", old_prefix="PID_"))
            # for ikey, ival in idict.items():
            #     print("ikey:", ikey, "ival:", ival)
            #     print("Type of ikey:",type(ikey), "Type of ival:", type(ival))
            if output_class == Player or output_class == Enemy:
                my_dict[idict["roman"]] = output_class.from_dict(input_dict=idict)
            if output_class == Skill:
                translate_output = translate_jp_to_en(idict, is_skill=True)
                if translate_output != None:
                    my_dict[translate_output] = output_class.from_dict(input_dict=idict)
            my_dict2[idict["id_tag"]] = output_class.from_dict(input_dict=idict)
        print("\n")
        return my_dict, my_dict2

    def process_data(data_loc, output, output_class):
        total = int()

        for file in os.listdir(data_loc):
            dprint("Processing:", file)
            with open(data_loc + "/" + file, "r", encoding="utf-8") as json_data:
                output[file.replace(".json", "")] = json.load(json_data)
                dprint(len(output[file.replace(".json", "")]), str(output_class.__name__), "entries found")
                total += len(output[file.replace(".json", "")])

        dprint("Total:", total, "entries for", str(output_class.__name__))
        print("\n")

        # dictionary to list of dictionary's values
        myList = []
        for key in output:
            myList.extend(output[key])

        # print("mylist length:", len(myList))

        # print(len(players))

        output = my_merger2(myList, output_class)
        return output

    os.chdir(r"/Resources/data/assets/Common/SRPG")
    dprint(os.listdir())
    # dictionary of json files converted to dicts
    # keys are json file names strings, values are lists of dictionaries which contain FEH skills
    skills = {}
    players = {}
    enemies = {}
    weapons = {}

    if get_skills:
        skills = process_data("Skill", skills, Skill)

    if get_characters:
        players = process_data("Person", players, Player)

        # ===========================================

        enemies = process_data("Enemy", enemies, Enemy)

    if get_weapons:
        with open("Weapon.json", "r", encoding="utf-8") as json_data:
            weapons["Weapon.json".replace(".json", "")] = json.load(json_data)

    stop = time()
    print("Time elapsed:", stop - start, "secs")
    return skills, players, enemies, weapons, english_data


if __name__ == "__main__":
    skills, players, enemies, weapons, english_data = load_files()

    print(players[0])
    print(players[1])

    print(players[0]["MARTH"].id_tag)

    print(enemies[0])
    print(enemies[1])

    from pprint import pprint

    pprint(skills[0])
    print(skills[1])

    print(skills[1]["SID_ジークリンデ"].skill_params)

    print(len(skills[0]), len(skills[1]))
    print("Difference:", abs(len(skills[0]) - len(skills[1])))


    def translate_jp_to_en(input_dict, tag="id_tag", prefix="MSID_", old_prefix="SID_", is_skill=False):

        if is_skill:
            output = None
            try:
                if input_dict.refined:
                    # removes refinement suffixes like _ATK or _DEF
                    # skillsDict[skill].id_tag.split("_")[0:-1]
                    # skillsDict[skill].roman_name = english_data[skillsDict[skill].refine_base.replace("SID_", "MSID_")]
                    output = str(translate_jp_to_en(input_dict, tag="refine_base")) + "_" + (
                    input_dict.id_tag.split("_")[-1])
                    dprint("Output1 here:", output)
                else:
                    try:
                        # x = repr((skill, ":", english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]))
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]
                        output = translate_jp_to_en(input_dict)
                        dprint("Output2 here:", output)
                        # output 2 seems to be skills, simple weapons and a few select prfs, specials, and some assists

                    except KeyError as e:
                        # print(i)
                        # print("Using MSID_H instead")
                        # print(skillsDict[i].id_tag.replace("SID_", "MSID_H_"))
                        dprint("\n")

                        if input_dict.beast_effect_id is not None and input_dict.category == 8:
                            output = translate_jp_to_en(input_dict, prefix="MSID_H_")
                            dprint(input_dict.id_tag)
                            dprint("Output4:", output)
                            return None

                        # dprint("Beast effect id:", input_dict["beast_effect_id"], "Category:", input_dict["category"])
                        # this means it's a duo effect or something similar (beast effect?), doesn't catch all duos
                        if input_dict.beast_effect_id is None and input_dict.category == 8:
                            # duo skills don't have names, but they do have descriptions
                            # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]

                            if input_dict.wep_equip == 0 and input_dict.skill_range == 0:
                                # print("Beast thing, not touching it")
                                return None

                            dprint("Duo Effect:", english_data[input_dict.id_tag.replace("SID_", "MSID_H_")])
                            # print(skillsDict[skill].id_tag.replace("SID_", "MSID_H_"))

                            # if hex(skillsDict[skills].wep_equip) & hex(weapon_index)

                            return None

                        if input_dict.id_tag == "SID_無し":
                            return "blank"

                        # y = repr((skill, ":", english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_H_")]))
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_H_")]

                        if input_dict.category != 7:
                            output = translate_jp_to_en(input_dict, prefix="MSID_H_")
                        dprint(input_dict.id_tag)
                        dprint("Output3:", output)
                        dprint("\n")
                        pass

                # anotherDict[output] = input_dict.id_tag
                return output
                # print(cur_skill.id_tag, ":", cur_skill.roman_name)

            except KeyError as e:
                print("Error:", e)
            pass
        else:
            return english_data[getattr(input_dict, tag).replace(old_prefix, prefix)]
        raise Exception("How did you get here")


    dprint(len([i for i in skills[0] if skills[0][i].id_tag in skills[1]]))

    counter = int()
    swapped = {skills[0][i].id_tag for i in skills[0]}
    for i in skills[1]:
        if not i in swapped:
            dprint(i)
            counter += 1
    dprint("Total:", counter)

    dprint("\n")

    skill0falcCounter = int()
    falcList0 = list()
    for i in skills[0]:
        if "Falchion" in i:
            dprint("skills[0] falchion:", i, "id_tag:", skills[0][i].id_tag)
            skill0falcCounter += 1
            falcList0.append(skills[0][i].id_tag)
    dprint("skills[0] total:", skill0falcCounter)

    dprint("")

    skill1falcCounter = int()
    falcList1 = list()
    for i in skills[1]:
        if "ファルシオン" in i:
            dprint("skills[1] falchion:", i)
            skill1falcCounter += 1
            falcList1.append(i)
    dprint("skills[1] total:", skill1falcCounter)

    dprint("Difference:", skill1falcCounter - skill0falcCounter)
    dprint([i for i in falcList1 if not i in falcList0])

    skill0burstCounter = int()
    burstList0 = list()
    for i in skills[0]:
        if "Umbra Burst" in i:
            dprint("skills[0] Umbra Burst:", i, "id_tag:", skills[0][i].id_tag)
            skill0burstCounter += 1
            burstList0.append(skills[0][i].id_tag)
    dprint("skills[0] total:", skill0burstCounter)

    dprint("")

    skill1burstCounter = int()
    burstList1 = list()
    for i in skills[1]:
        if "影没の波動" in i:
            dprint("skills[1] Umbra Burst:", i)
            skill1burstCounter += 1
            burstList1.append(i)
    dprint("skills[1] total:", skill1burstCounter)

    dprint("Difference:", skill1burstCounter - skill0burstCounter)
    dprint([i for i in burstList1 if not i in burstList0])

    trans_list = []
    trans_set = set()
    for i in skills[1]:
        val = translate_jp_to_en(skills[1][i], is_skill=True)
        trans_list.append(val)
        trans_set.add(val)

    dprint("None in trans_set:", True if None in trans_set else False)
    dprint("Missiletainn count:", trans_list.count("Missiletainn"))

    dprint(len(trans_list))
    dprint(len(trans_set))
    dprint(trans_list.count(None))
    counter = int()
    for i in trans_list:
        if i is not None:
            if "Falchion" in i:
                dprint(i)
                counter += 1
    dprint("Total:", counter)

    dprint([val for val in trans_list if val not in trans_set])

    for val in trans_set:
        trans_list.remove(val)

    for _ in range(trans_list.count(None)):
        trans_list.remove(None)

    removeList = []
    for i in trans_list:
        if "Falchion" in i:
            removeList.append(i)

    for i in removeList:
        trans_list.remove(i)

    dprint(len(trans_list))

    dprint(trans_list)

    # CONCLUSION: some things, like Falchion, get overridden, others cannot be translated by current translation method
    # List: 3515, Set: 3400 --> 3400 translated normally; 96 untranslated, set as None; 11 overridden Falchion items;
    # 7 Umbra Burst? Also 1 Missiletainn, but I think that's because the game has 2 separate Missiletainn weapons,
    # those being the sword (used by Owain) and the tome (used by Ophelia), so that one doesn't count

    # pprint([i for i in skills])
    # print(len(skills["00_first"]))
    # for i in skills["00_first"]:
    #     print("")
    #     print(i)
    #     for j in i:
    #         try:
    #             print(j, ":", i[j])
    #         except TypeError as e:
    #             # print(e)
    #             pass
    #     print("")
    # pprint([i for i in characters])
    # pprint([i for i in weapons])
