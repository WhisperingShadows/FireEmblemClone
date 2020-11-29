from Code.FireEmblemCombatV2 import *


# TODO: Change to programmatically generate slid functions and arguments to reduce repetition

def slid1(user: Character):
    if user.is_initiating:
        return 1
    return 0


def slid2(user: Character):
    if user.is_initiating:
        return 0
    return 1


def slid3(skill: Skill, user: Character):
    slid = find(skill, 3)
    if hp_between(slid.param1, slid.param2, user):
        return 1
    return 0


def slid4(skill: Skill, turn: int):
    slid = find(skill, 4)
    if slid.param1 == 0:
        return 1 if turn == (1 - slid.param2) else 0

    elif slid.param1 > 0:
        return 1 if (turn - 1) % slid.param1 == slid.param2 else 0

    raise ValueError("Invalid value {0} supplied by SLID param1. Must be positive integer.".format(slid.param1))


def slid5(skill: Skill, foe: Character):
    slid = find(skill, 5)
    if hp_between(slid.param1, slid.param2, foe):
        return 1
    return 0


def slid6():
    return 1


def slid7(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 7)
    if foe.stat_difference(slid.param1, user) >= slid.param2:
        return 1
    return 0


def slid9(skill: Skill, foe: Character):
    if skill.skill_targets(foe):
        return 1
    return 0


def slid11(skill: Skill, user: Character):
    slid = find(skill, 11)
    # minus one accounts for exclusion of foe from calculations
    if count_around(user, foes, slid) - 1 >= count_around(user, allies, slid) + slid.param2:
        return 1
    return 0


def slid13(skill: Skill, user: Character):
    slid = find(skill, 13)
    # minus one accounts for exclusion of foe from calculations
    # count_around takes output of within_range, which includes foe, but not user
    # maybe try using lambda nearby: foes([i for i in nearby if i is not foe])
    if count_around(user, allies, slid) >= count_around(user, foes, slid) - 1 + slid.param2:
        return 1
    return 0


def slid14(skill: Skill, user: Character):
    slid = find(skill, 14)
    if count_around(user, allies, slid) >= slid.param2:
        return 1
    return 0


def slid15(skill: Skill, foe: Character):
    wep_weaknesses = filter_true_indexes(convert_to_bitmask_list(skill.wep_weakness))
    for foe_skill in foe.equipped_skills:
        assert isinstance(foe_skill, Skill)
        for index in wep_weaknesses:
            if in_bitmask(index, foe_skill.wep_effective):
                break
        else:
            continue
        break
    else:
        return 0
    return 1


def slid19(skill: Skill, user: Character):
    slid = find(skill, 14)
    if count_around(user, allies, slid) <= slid.param2:
        return 1
    return 0


# TODO: Write status-checking code
def slid21(skill: Skill, user: Character):
    """
    param1 = 1, param2 = 0: If  Bonus is active on unit
    param1 = 1, param2 = 1: If  March is active on unit
    param1 = 1, param2 = 2: If【Bonus】is active on unit

    :param user:
    :return:
    """
    slid = find(skill, 21)
    if slid.param1 == 1:
        # TODO: Add functionality to keys 1 and 2
        out = {0: bonus_narrow(user), 1: user.status_effects["March"], 2: bonus_broad(user)}.get(slid.param2)
        return 1 if out else 0
    return 0


def slid22(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 22)
    if user.stat_difference(slid.param1, foe) >= slid.param2:
        return 1
    return 0


def slid23(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 22)
    if user.stat_difference(slid.param1, foe) <= slid.param2:
        return 1
    return 0


def slid24(user: Character):
    if user.special_cd == 0:
        return 1
    return 0


def slid25(foe: Character):
    return penalty_broad(foe)


def slid27(skill: Skill, user: Character):
    slid = find(skill, 27)
    if penalty_broad(user) or hp_between(slid.param1, slid.param2, user):
        return 1
    return 0


def slid28(user: Character, foe: Character):
    if user.calc_weapon_triangle(foe) > 0:
        return 1
    return 0


def slid29(skill: Skill, user: Character):
    slid = find(skill, 29)
    # CHECK: now I think this ought to work, but I've learned not to trust myself
    if count_around(user, lambda items, unit: not_dragon(not_beast(allies(items, unit))), slid) <= slid.param2:
        return 1
    return 0


def slid32(foe: Character):
    return not bonus_narrow(foe)


def slid33(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 33)
    if (hp_between(slid.param1, slid.param2, user) and hp_between(slid.param1, slid.param2, foe)) \
            or (not hp_between(slid.param1, slid.param2, user) and not hp_between(slid.param1, slid.param2, foe)):
        return 1
    return 0


def slid34(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 34)
    if buff_total(user) + debuff_total(foe) >= slid.param1:
        return 1
    return 0


def slid36(skill: Skill, user: Character):
    slid = find(skill, 36)
    if slid.param1 == 1:
        if bonus_narrow(user):
            return 1
    if slid.param2 == 1:
        if user.status_effects["March"] == True:
            return 1
    return 0


def slid37(skill: Skill, foe: Character):
    slid = find(skill, 37)
    if penalty_broad(foe) or hp_between(slid.param1, slid.param2, foe):
        return 1
    return 0


def slid38(skill: Skill, foe: Character, turn: int):
    slid = find(skill, 38)
    if turn % 2 == 1 or hp_between(slid.param1, slid.param2, foe):
        return 1
    return 0


def slid39(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 39)
    if user.stats["hp"] >= foe.hp + slid.param2:
        return 1
    return 0


def slid40(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 40)
    if user.status_effects["March"] or user.stat_difference(slid.param1, foe) >= slid.param2:
        return 1
    return 0


def slid41(foe: Character):
    if foe.is_initiating or not bonus_narrow(foe):
        return 1
    return 0


def slid42(skill: Skill, user: Character):
    slid = find(skill, 42)
    if hp_between(slid.param1, slid.param2, user):
        return 1
    return 0


def slid43(skill: Skill, user: Character):
    slid = find(skill, 43)
    if penalty_broad(user) or hp_between(slid.param1, slid.param2, user):
        return 1
    return 0


def slid44(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 44)
    if user.stat_difference(slid.param1, foe) >= slid.param2:
        return 1
    return 0


def slid45(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 45)
    if user.stat_difference(hundreds(slid.param1), foe) >= tens_ones(slid.param1) or \
            hp_between(slid.param2, 100, foe):
        return 1
    return 0


def slid46(skill: Skill, foe: Character):
    slid = find(skill, 46)
    if foe.is_initiating or hp_between(slid.param1, slid.param2, foe):
        return 1
    return 0


def slid47(skill: Skill, user: Character):
    slid = find(skill, 47)
    if count_around(user, lambda items: [i for i in allies(items, user) if i.has_acted], slid) >= slid.param2:
        return 1
    return 0


def slid48(skill: Skill, user: Character):
    slid = find(skill, 48)
    if bonus_narrow(user) or hp_between(slid.param1, slid.param2, user):
        return 1
    return 0


def slid49(skill: Skill, user: Character):
    slid = find(skill, 49)
    if count_around(user, lambda items: [i for i in allies(items, user) if buff_total(i)
                                                                           >= tens_ones(slid.param1)],
                    slid) >= hundreds(slid.param2):
        return 1
    return 0


def slid50(skill: Skill, user: Character):
    slid = find(skill, 50)
    # wowza, that's something alright
    return True in [i for i in allies(within_range_abstracted(
        user, None, "within_range", distance_override=slid.param1), user) if hp_between(0, slid.param2, i)]


def slid51(skill: Skill, user: Character):
    slid = find(skill, 51)
    if bonus_narrow(user) or count_around(user, allies, slid) >= slid.param2:
        return 1
    return 0


def slid52(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 52)
    if foe.is_initiating or hp_between(slid.param1, slid.param2, user):
        return 1
    return 0


def slid54(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 54)
    if skill.skill_targets(foe) or hp_between(slid.param1, slid.param2, user):
        return 1
    return 0


def slid56(skill: Skill):
    # man, fuck this, I'll put it in later
    # can't believe I have to add an entire new variable just for one skill
    return 0


def slid57(skill: Skill, user: Character, foe: Character):
    slid = find(skill, 57)
    if hp_between(slid.param1, slid.param2, user) or hp_between(slid.param1, slid.param2, foe):
        return 1
    return 0


def said11(self):
    pass


def said13(self):
    pass


def said22(self):
    pass


def said35(self):
    pass


def said36(self):
    pass


def said37(self):
    pass


def said41(self):
    pass


def said42(self):
    pass


def said43(self):
    pass


def said44(self):
    pass


def said46(self):
    pass


def said47(self):
    pass


def said48(self):
    pass


def said57(self):
    pass


def said59(self):
    pass


def said60(self):
    pass


def said62(self):
    pass


def said63(self):
    pass


def said64(self):
    pass


def said66(self):
    pass


def said70(self):
    pass


def said76(self):
    pass


def said77(self):
    pass


def said78(self):
    pass


def said79(self):
    pass


def said82(self):
    pass


def said84(self):
    pass


def said85(self):
    pass


def said90(self):
    pass


def said91(self):
    pass


def said93(self):
    pass


def said95(self):
    pass


def said97(self):
    pass


def said104(self):
    pass


def said113(self):
    pass


def said115(self):
    pass


def said116(self):
    pass


def said117(self):
    pass


def said119(self):
    pass


def said120(self):
    pass


def said121(self):
    pass


def said126(self):
    pass


def said127(self):
    pass


def said128(self):
    pass


def said129(self):
    pass


def said130(self):
    pass


def said135(self):
    pass


def said136(self):
    pass


def said137(self):
    pass


def said138(self):
    pass


def said140(self):
    pass


def said142(self):
    pass


def said144(self):
    pass


def said145(self):
    pass


def said146(self):
    pass


def said150(self):
    pass


def said151(self):
    pass


def said152(self):
    pass


def said154(self):
    pass


def said155(self):
    pass


def said157(self):
    pass


def said162(self):
    pass


def said163(self):
    pass


def said164(self):
    pass


def said167(self):
    pass


def said169(self):
    pass


def said171(self):
    pass


def said172(self):
    pass


def said173(self):
    pass


def said176(self):
    pass


def said178(self):
    pass


def said179(self):
    pass


def said181(self):
    pass


def said182(self):
    pass


def said183(self):
    pass


def said184(self):
    pass


def said187(self):
    pass


def said188(self):
    pass


def said189(self):
    pass


def said190(self):
    pass


def said191(self):
    pass


def said193(self):
    pass


def said194(self):
    pass


def said196(self):
    pass


def said198(self):
    pass


def said199(self):
    pass


def said201(self):
    pass


def said202(self):
    pass


def said208(self):
    pass


def said210(self):
    pass


def said212(self):
    pass


def said213(self):
    pass


def said220(self):
    pass
