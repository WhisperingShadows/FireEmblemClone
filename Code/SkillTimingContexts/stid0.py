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


def slid9(skill: Skill, target: Character, ):
    if skill.skill_targets(target):
        return 1
    return 0


def said17(skill: Skill, unit: Character, target: Character):
    """
    Shove/smite assist

    :param unit:
    :param target:
    :return:
    """

    # FIXME: get_direction does not return a magnitude 1 vector, this logic is invalid
    target.move_direction(get_direction(unit, target), skill.skill_params["hp"])


def said18(skill: Skill, unit: Character, target: Character):
    """
    Swap assist

    :param unit:
    :param target:
    :return:
    """
    temp = unit.pos
    unit.move(target.pos)
    target.move(temp)

    # FIXME: Additional action should be granted once per turn only.
    if skill.skill_params["res"] == 1:
        give_action(unit)


def said19(skill: Skill, unit: Character, target: Character):
    """
    Drawback assist

    :param unit:
    :param target:
    :return:
    """
    temp = unit.pos
    unit.move_direction(get_direction(target, unit), 1)
    target.move(temp)


def said20(skill: Skill, unit: Character, target: Character):
    """
    Reposition / To Change Fate (Chrom) assist

    :param unit:
    :param target:
    :return:
    """
    target.move_direction(get_direction(target, unit), 2)
    if skill.skill_params["res"] == 2:
        give_action(unit)
        # FIXME
        # (Additional action granted once per turn only.) Grants Atk+6 to unit and
        # Pair Up cohort for 1 turn. ADD_STATUS( Isolation; unit and Pair Up cohort).


def said21(skill: Skill, unit: Character, target: Character):
    """
    Pivot assist

    :param unit:
    :param target:
    :return:
    """
    unit.move_direction(get_direction(unit, target), 2)


def said22(skill: Skill, unit: Character, target: Character):
    # CHECK: is this section supposed to be executed always or only when spd param == 0?
    hp_add = max(skill.skill_params["def"] / 100 * unit.stats["atk"] + skill.skill_params["res"],
                 skill.skill_params["hp"])
    map_add_hp(hp_add, target)
    map_add_hp(skill.skill_params["atk"], unit)

    if skill.skill_params["spd"] == 1:
        map_add_hp(unit.stats["hp"] - unit.hp, target)
        map_add_hp((unit.stats["hp"] - unit.hp) * 0.5, unit)
    elif skill.skill_params["spd"] == 2:
        map_add_hp(max(0, target.stats["hp"] - (2 * target.hp)), target)
    elif skill.skill_params["spd"] == 3:
        neutralize_penalties(target)
        pass
    pass


def said23(skill: Skill, unit: Character, target: Character):
    to_buff = neighborhood(target, skill)
    to_buff.remove(unit)
    buff(skill, to_buff)


def said27(skill: Skill, unit: Character, target: Character):
    if skill.skill_params["hp"] > 0:
        map_add_hp(skill.skill_params["hp"], target)
        # CHECK: Check whether the above can donate the full hp amount and if not, give less in below
        map_add_hp(-skill.skill_params["hp"], unit)
    elif skill.skill_params["hp"] == -1:
        map_add_hp(unit.hp - 1, target)
        map_add_hp(1 - unit.hp, unit)
    if skill.skill_params["hp"] == 1:
        convert_penalties_to_bonuses(target)


def said28(unit: Character, target: Character):
    temp = unit.hp
    unit.hp = min(target.hp, unit.stats["hp"])
    target.hp = min(temp, target.stats["hp"])


def said29(skill: Skill, target: Character):
    convert_penalties_to_bonuses(target)
    if skill.skill_params["hp"] == 1:
        neutralize_penalties(target)


def said30(skill: Skill, unit: Character, target: Character):
    # CHECK: Check if target is a refresher here or put that in the give_action func?
    give_action(target)

    # TODO: Use switch-equivalent dict for this
    if skill.skill_params["res"] == 1:
        if skill.skill_targets(target):
            add_status("March", target)
    elif skill.skill_params["res"] == 2:
        affected_units = neighborhood_ex(unit, None, "in_cardinals")
        affected_units.extend(neighborhood_ex(target, None, "in_cardinals"))
        affected_units.remove(unit)

        spectrum_buff(affected_units, skill.skill_params["atk"])
        for aff_unit in affected_units:
            add_status(status(skill.skill_params["hp"]), aff_unit)
    elif skill.skill_params["res"] == 3:
        pass
    elif skill.skill_params["res"] == 4:
        pass
    elif skill.skill_params["res"] == 5:
        pass
    pass


def said55(self):
    pass


def said56(self):
    pass


def said67(skill: Skill, unit: Character):
    # cooldown(skill.skill_params["hp"], unit)

    for character in skill.targeted(allies(within_range_ex_abstract(unit, skill), unit)):
        cooldown(skill.skill_params["hp"], character)


def said88(skill: Skill, unit: Character):
    """BUFF(unit and TARGETED(allies WITHIN_RANGE_EX(unit))).
    ADD_STATUS(STATUS(skill_params.hp); unit and TARGETED(allies WITHIN_RANGE_EX(unit)))"""

    for character in skill.targeted(allies(within_range_ex_abstract(unit, skill), unit)):
        buff(skill, character)
        add_status(status(skill.skill_params["hp"]), character)


def said92(skill: Skill, unit: Character):
    """MAP_ADD_HP(skill_params.hp; foes WITHIN_RANGE_EX(unit)).
    ADD_STATUS(STATUS(skill_params.atk); foes WITHIN_RANGE_EX(unit))"""

    for character in foes(within_range_ex_abstract(unit, skill), unit):
        map_add_hp(skill.skill_params["hp"], character)
        add_status(status(skill.skill_params["atk"]), character)


def said192(skill: Skill, unit: Character):
    """MAP_ADD_HP(skill_params.hp; NEIGHBORHOOD_EX(unit)).
    Neutralizes【Penalty】on NEIGHBORHOOD_EX(unit).
    BUFF(NEIGHBORHOOD_EX(unit))"""

    for character in neighborhood_ex(unit, skill):
        map_add_hp(skill.skill_params["hp"], character)
        neutralize_penalties(character)
        buff(skill, character)


def said200(skill: Skill, unit: Character):
    """BUFF(NEIGHBORHOOD_EX(unit)).
    ADD_STATUS(STATUS(skill_params.hp); NEIGHBORHOOD_EX(unit)).
    ADD_STATUS(STATUS(skill_params2.hp); NEIGHBORHOOD_EX(unit))"""

    for character in neighborhood_ex(unit, skill):
        buff(skill, character)
        add_status(status(skill.skill_params["hp"]), character)
        add_status(status(skill.skill_params2["hp"]), character)


def said214(skill: Skill, unit: Character):
    """ADD_STATUS(STATUS(skill_params.hp); NEIGHBORHOOD_EX(unit)).
    ADD_STATUS(STATUS(skill_params2.hp); foes WITHIN_RANGE_EX(unit)).
    BUFF2(foes WITHIN_RANGE_EX(unit))."""

    for character in foes(within_range_ex_abstract(unit, skill), unit):
        add_status(status(skill.skill_params2["hp"]), character)
        buff2(skill, character)

    for character in neighborhood_ex(unit, skill):
        add_status(status(skill.skill_params["hp"]), character)


def said217(skill: Skill, unit: Character):
    """ADD_STATUS(STATUS(skill_params.hp);
    unit and allies from the same titles WITHIN_RANGE_EX(unit))"""

    # TODO

    pass
