import json
import os
from pprint import pprint
from time import time


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


from collections import MutableMapping


def rec_merge(d1, d2):
    '''
    Update two dicts of dicts recursively,
    if either mapping has leaves that are non-dicts,
    the second's leaf overwrites the first's.
    '''
    for k, v in d1.items():  # in Python 2, use .iteritems()!
        if k in d2:
            # this next check is the only difference!
            if all(isinstance(e, MutableMapping) for e in (v, d2[k])):
                d2[k] = rec_merge(v, d2[k])
            # we could further check types and merge as appropriate here.
    d3 = d1.copy()
    d3.update(d2)
    return d3


def load_files(get_english_data=True, get_skills=True, get_characters=True, get_weapons=True):
    # print("Starting")
    start = time()

    if get_english_data:
        os.chdir(r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\data\assets\USEN\Message\Data")

        english_data = {}
        total = int()
        for file in os.listdir():
            print("Processing:", file)
            with open(file, "r", encoding="utf-8") as json_data:
                english_data[file.replace(".json", "")] = json.load(json_data)
                print(len(english_data[file.replace(".json", "")]))
                total += len(english_data[file.replace(".json", "")])
        print("Total:", total)
        total = int()
        for i in english_data:
            print(len(english_data[i]))
            total += len(english_data[i])
        print("Total:", total)

        myList = []
        # extra = {k: v for d in english_data for k, v in d.items()}
        for key in english_data:
            myList.extend(english_data[key])

        print("mylist length:", len(myList))

        # extra = {k: v for d in myList for k, v in d.items()}
        # print(len(extra))

        # from functools import reduce
        # english_data = reduce(rec_merge, [dict(i = english_data[i]) for i in english_data])["i"]

        print(len(english_data))

        # wicked cool list comprehension but it's about 1.6x slower than using my_merger()
        # new_var = {var[0]: var[1] for var in [(eng_dict["key"], eng_dict["value"]) for eng_dict in english_data]}

        def my_merger(list_of_dicts):
            my_dict = {}
            for idict in list_of_dicts:
                my_dict[idict["key"]] = idict["value"]
            return my_dict

        # english_data = my_merger(english_data)
        english_data = my_merger(myList)

    os.chdir(r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\data\assets\Common\SRPG")
    print(os.listdir())
    # dictionary of json files converted to dicts
    # keys are json file names strings, values are lists of dictionaries which contain FEH skills
    skills = {}
    characters = {}
    weapons = {}

    if get_skills:
        for file in os.listdir("Skill"):
            # print(file)
            with open(r"Skill/" + file, "r", encoding="utf-8") as json_data:
                skills[file.replace(".json", "")] = json.load(json_data)

        # for skillDict in skills["200702_monsyou"]:
        #
        #     classSkill = Skill.from_dict(skillDict)
        #     # pprint(classSkill.stats)
        #     print(classSkill.stats["def"])

    if get_characters:
        for file in os.listdir("Person"):
            # print(file)
            with open(r"Person/" + file, "r", encoding="utf-8") as json_data:
                characters[file.replace(".json", "")] = json.load(json_data)

    if get_weapons:
        with open("Weapon.json", "r", encoding="utf-8") as json_data:
            weapons["Weapon.json".replace(".json", "")] = json.load(json_data)

    stop = time()
    print("Time elapsed:", stop - start, "secs")
    return skills, characters, weapons, english_data


def translate_jp_to_en(text, tag="id_tag", prefix="MSID_"):
    return english_data[getattr(text, tag).replace("SID_", prefix)]


if __name__ == "__main__":
    skills, characters, weapons, english_data = load_files()

    skillsDict = {}
    secDict = {}
    for file in skills:
        for skill in skills[file]:
            secDict[skill["id_tag"]] = skill

            skillsDict[skill["id_tag"]] = Skill.from_dict(input_dict=skill)

    # print(english_data["MSID_H_ダメージ強化R差分"])

    anotherDict = {}

    counter = int()
    error_counter = int()
    for skill in skillsDict:
        cur_skill = skillsDict[skill]
        counter += 1
        try:
            if cur_skill.refined:
                # removes refinement suffixes like _ATK or _DEF
                # skillsDict[skill].id_tag.split("_")[0:-1]
                # skillsDict[skill].roman_name = english_data[skillsDict[skill].refine_base.replace("SID_", "MSID_")]
                cur_skill.roman_name = translate_jp_to_en(cur_skill, tag="refine_base")
            else:
                try:
                    # x = repr((skill, ":", english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]))
                    # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]
                    cur_skill.roman_name = translate_jp_to_en(cur_skill)

                except KeyError as e:
                    # print(i)
                    # print("Using MSID_H instead")
                    # print(skillsDict[i].id_tag.replace("SID_", "MSID_H_"))
                    print("\n")

                    print("Beast effect id:", cur_skill.beast_effect_id, "Category:", cur_skill.category)
                    # this means it's a duo effect or something similar
                    if cur_skill.beast_effect_id == None and cur_skill.category == 8:
                        print("Current errors:", error_counter)
                        # duo skills don't have names, but they do have descriptions
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]

                        if cur_skill.wep_equip == 0 and cur_skill.skill_range == 0:
                            # print("Beast thing, not touching it")
                            continue

                        print("Duo Effect:", english_data[cur_skill.id_tag.replace("SID_", "MSID_H_")])
                        # print(skillsDict[skill].id_tag.replace("SID_", "MSID_H_"))

                        # if hex(skillsDict[skills].wep_equip) & hex(weapon_index)

                        continue
                        pass

                    if cur_skill.id_tag == "SID_無し":
                        cur_skill.roman_name = "blank"
                        continue

                    # y = repr((skill, ":", english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_H_")]))
                    # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_H_")]
                    cur_skill.roman_name = translate_jp_to_en(cur_skill, prefix="MSID_H_")
                    print("\n")
                    pass

            anotherDict[cur_skill.roman_name] = cur_skill.id_tag

            # print(cur_skill.id_tag, ":", cur_skill.roman_name)

        except KeyError as e:
            print("Error:", e)
            error_counter += 1

    print(error_counter, "skills out of", counter, "failed to translate")

    # print(skillsDict[anotherDict["Wings of Mercy 3"]].skill_params)

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
