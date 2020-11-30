from Code.FireEmblemCombatV2 import *

import os
import sys

main_file = os.path.abspath(sys.modules["__main__"].__file__)
imported_file = os.path.abspath(sys.modules["Code.FireEmblemCombatV2"].__file__)

if main_file == imported_file:
    module = sys.modules["__main__"]
else:
    module = sys.modules["Code.FireEmblemCombatV2"]

# iterates over items defined in given module and copies them into the local
# namespace if they are functions or classes
for item_name in dir(module):
    # if item_name is not a special global variable like __name__
    if not item_name.startswith("__"):
        # moves item directly into local namespace by copying original
        exec(f"{item_name} = getattr(module, item_name)")


def slid3(skill: Skill, unit: Character):
    """
    At start of turn, if hp_between(param1; param2; unit)

    :param unit:
    :return:
    """

    slid = find(skill, 3)
    if hp_between(slid.param1, slid.param2, unit):
        return True
    return False


def slid4(skill: Skill, **kwargs):
    """
    param1 = 0: At the start of turn (1 − param2)
    param1 > 0: At start of turn x, if (x − 1) mod param1 = param2

    :return:
    """

    # TODO

    slid = find(skill, 4)
    if slid.param1 == 0:
        return True

    elif slid.param1 > 0:
        return

    pass


def slid7(skill: Skill, unit: Character, target: Character):
    """
    At start of turn, if stat_difference(param1; target) ≥ param2

    :param unit:
    :param target:
    :return:
    """
    slid = find(skill, 7)

    if unit.stat_difference(slid.param1, target) >= slid.param2:
        return True
    return False


def slid9(skill: Skill, target: Character):
    """
    If skill_targets(target)

    :param target:
    :return:
    """

    if skill.skill_targets(target):
        return 1
    return 0


def slid10(skill: Skill, target: Character):
    pass


def slid14(skill: Skill, unit: Character):
    """
    At start of turn, if count_around(unit; allies) ≥ param2

    :param unit:
    :return:
    """

    if count_around(unit, allies, skill.slid) >= skill.slid.param2:
        return True
    return False

    pass


def slid19(skill: Skill, unit: Character):
    """
    At start of turn, if count_around(unit; allies) ≤ param2

    :param unit:
    :return:
    """

    if count_around(unit, allies, skill.slid) <= skill.slid.param2:
        return True
    return False

    pass


def slid30(skill: Skill, unit: Character):
    """
    At start of turn, if count_around(unit; allies (excluding dragon allies)) ≤ param2

    :param unit:
    :return:
    """

    if count_around(unit, lambda chars, u: not_dragon(allies(chars, u)),
                    skill.slid) <= skill.slid.param2:
        return True
    return False


def slid31(skill: Skill, unit: Character):
    """
    At start of turn, if count_around(unit; dragon or beast allies) ≥ param2

    :param unit:
    :return:
    """

    if count_around(unit, lambda chars, u: dragon(chars) + beast(chars),
                    skill.slid) >= skill.slid.param2:
        return True
    return False

    pass


def slid35(unit: Character):
    """
    At start of turn, if special cooldown count is at its maximum value

    :return:
    """

    if unit.special_cd == unit.max_special_cd:
        return True
    return False

    pass


def said22(skill: Skill, unit: Character):
    """
    At start of turn, map_add_hp(skill_params.hp; neighborhood(unit)).

    :param unit:
    :return:
    """

    for char in neighborhood(unit, skill):
        map_add_hp(skill.skill_params["hp"], char)


def said23(skill: Skill, unit: Character):
    """
    At start of turn, buff(neighborhood(unit)).

    :param unit:
    :return:
    """

    for char in neighborhood(unit, skill):
        buff(skill, char)


def said50(skill: Skill, unit: Character):
    """
    At start of turn, map_add_hp(skill_params.hp; allies within_range(unit)).

    :param unit:
    :return:
    """

    for char in allies(within_range_abstracted(unit, skill), unit):
        map_add_hp(skill.skill_params["hp"], char)

    pass


def said51(skill: Skill, unit: Character):
    """
    At start of turn, map_add_hp(skill_params.hp; foes within_range(unit)).

    :param unit:
    :return:
    """

    for char in foes(within_range_abstracted(unit, skill), unit):
        map_add_hp(skill.skill_params["hp"], char)

    pass


def said52(skill: Skill, unit: Character):
    """
    At start of turn, buff(targeted(allies within_range(unit))).

    :param unit:
    :return:
    """

    for char in skill.targeted(allies(within_range_abstracted(unit, skill), unit)):
        buff(skill, char)

    pass


def said53(skill: Skill, unit: Character):
    """
    At start of turn, buff(targeted(foes within_range(unit))).

    :param unit:
    :return:
    """

    for char in skill.targeted(foes(within_range_abstracted(unit, skill), unit)):
        buff(skill, char)

    pass


def said67(skill: Skill, unit: Character):
    """
    At start of turn, map_add_hp(skill_params.atk; unit) and cooldown(skill_params.hp; unit).

    :param unit:
    :return:
    """

    map_add_hp(skill.skill_params["atk"], unit)
    cooldown(skill.skill_params["hp"], unit)

    pass


def said68(skill: Skill, unit: Character):
    """
    At start of turn, buff(foes in cardinal directions of unit).

    :param unit:
    :return:
    """

    within_range_abstracted()
    within_range_ex_abstract()

    pass


def said69(self):
    pass


def said73(self):
    pass


def said74(self):
    pass


def said86(self):
    pass


def said88(self):
    pass


def said89(self):
    pass


def said92(self):
    pass


def said98(self):
    pass


def said105(skill: Skill, unit: Character):
    """
    At start of turn, COOLDOWN(−number of TARGETED(allies on team (including unit)); unit).

    :return:
    """

    cooldown(-len(skill.targeted(allies(char_list, unit))), unit)

    pass


def said106(self):
    pass


def said111(self):
    pass


def said114(self):
    pass


def said118(self):
    pass


def said122(self):
    pass


def said123(self):
    pass


def said125(self):
    pass


def said131(self):
    pass


def said132(self):
    pass


def said133(self):
    pass


def said141(self):
    pass


def said159(self):
    pass


def said195(self):
    pass


def said203(self):
    pass


def said207(self):
    pass
