from Code.FEH_character_search import get_character
from Code.ThreadedLoad_JSON_Data import load_files

skills_data, players_data, enemies_data, weapons_data, english_data, growth_data, move_data, \
stage_encount_data, terrain_data = load_files(True, False, True, False, get_simple_names=True)


# def zip_op(t1, t2, op):
#     z = []
#     for i in range(len(t1)):
#         z.append(op(t1[i], t2[i]))
#     return z

def zip_op(t1, t2, op):
    return [*map(lambda i: op(i[0], i[1]), zip(t1, t2))]


def generate_(n, f):
    z = []
    for i in range(1, n + 1):
        z.append(f(i))
    return z


def map_(t, f):
    z = []
    for i in range(0, len(t)):
        z.append(f(t[i], i))

    return z


def count_if_(t, pr):
    z = 0

    for i in range(0, len(t)):
        if pr(t[i], i):
            z += 1

    return z


def arrayOrder_(arr):
    return map_(arr, lambda lhs, i:
    count_if_(arr, lambda rhs, j:
    (i < j and lhs >= rhs) or (i > j and lhs > rhs)
              )
                )


# arr = [1,3,2,4,3,3]
#
# for index, data in enumerate(arrayOrder_(arr)):
#     print(index+1, data, arr[data])

STAT_dict = {0: "hp", 1: "atk", 2: "spd", 3: "def", 4: "res"}
StatOffset = {"hp": -35, "atk": -28, "spd": -21, "def": -14, "res": -7}

import math


def get_applied_growth_rate(rarity, rate):
    return math.floor(rate * (0.79 + 0.07 * rarity))


def get_growth_value(rarity, rate):
    return math.floor(0.39 * get_applied_growth_rate(rarity, rate))


def getSupergrowth(rarity, rate):
    neut = get_growth_value(rarity, rate)
    if get_growth_value(rarity, rate + 5) > neut + 2:
        return 1
    elif get_growth_value(rarity, rate - 5) < neut - 2:
        return -1
    return 0


def get_rarity_bonuses(five_star_lv1_stats):
    # var = arrayOrder_(five_star_lv1_stats[2 - 1:])
    # var.insert(0, 0)
    # order = var
    order = [0, *arrayOrder_(five_star_lv1_stats[2 - 1:])]
    return generate_(5, lambda rarity:
    [*map(lambda o:
          2 - math.floor((5 - rarity + (o < 2)) / 2),
          order)]
                     )


def rarity_bonuses_for_3_stars(rarity_bonuses, rarity):
    return {k: v for k, v in zip(STAT_dict.values(), [i - 1 for i in rarity_bonuses[rarity - 1]])}


def convert_lv1_3star_stats_to_5star(stats):
    """
    This just adds 1 to each stat?

    :param stats:
    :return:
    """
    if isinstance(stats, int):
        return stats + 1
    else:
        if len(stats) != 5:
            raise Exception("Invalid number of stats supplied, should be 5")
        else:
            new_stats = []
            for stat in stats:
                stat += 1
                new_stats.append(stat)
            return new_stats


def full_lv1_stats(five_star_lv1_stats):
    """
    Returns level 1 stats at all rarities

    :param five_star_lv1_stats:
    :return:
    """
    var = arrayOrder_(five_star_lv1_stats[2 - 1:])
    # print("Order before unpack:", var)
    var.insert(0, 0)
    # print("Order after insert:", order)
    order = var
    # print("Order after unpack:", order)

    # order = unpack(arrayOrder(sub(fiveStarLv1Stats, 2, 5)))
    return generate_(5, lambda rarity:
    zip_op(five_star_lv1_stats, order, lambda b, o:
    b - math.floor((5 - rarity + (o < 2 and 1 or 0)) / 2)
           )
                     )


def full_lv40_stats(rate_set, full_1_stat_set):
    return map_(full_1_stat_set,
                lambda stat_set, rarity:
                zip_op(stat_set, rate_set, lambda base, rate:
                base + get_growth_value(rarity, rate)
                       )
                )


# not used for playable units at any level other than 40 where randomized stats converge
# mostly used for tempest trials, training tower, chain challenges, etc.
def general_levelup(new_level, old_level, applied_growth_rate):
    # returns growth value
    return math.trunc((new_level - old_level) * (applied_growth_rate * 0.01))


def get_growth_vector_id(five_star_lv1_neutral_base_stat, offset, applied_growth_rate, bvid):
    if isinstance(offset, int):
        num_offset = offset
    elif isinstance(offset, str):
        if offset in StatOffset:
            num_offset = StatOffset[offset]
        else:
            raise KeyError("Invalid stat key supplied")
    else:
        raise TypeError("Invalid offset supplied")

    return ((3 * five_star_lv1_neutral_base_stat) + num_offset + applied_growth_rate + bvid) % 64


def get_growth_vector(growth_value, growth_vector_id):
    # print(format(growth_data[growth_value][growth_vector_ID], "0b")[::-1][1:], "Formated Ver")
    # print(bin(growth_data[growth_value][growth_vector_ID])[::-1][1:].replace("b0", ""), "Bin ver 1")
    # print(bin(growth_data[growth_value][growth_vector_ID])[1:-1][::-1], "Bin ver 2") # still has b at the end
    bin_string = format(growth_data[growth_value][growth_vector_id], "0b")[::-1][1:]
    output = bin_string + "0" * (40 - len(bin_string))
    return output


def test_growth_vector(growth_vector, base, lv40):
    # print(growth_vector)
    # print(list(growth_vector).count("1"))
    return base + list(growth_vector).count("1") == lv40


# vec_id = get_growth_vector_id(18, -35, get_applied_growth_rate(5, 45), 169)
# print(get_growth_vector(19, vec_id))

def get_stat_increase_for_level_abstract_fill(char, stat, rarity=None, level=None,
                                              stats=None, rates=None,
                                              bvid=None, asset=None, flaw=None):
    rarity = char.rarity if rarity is None else rarity
    level = char.level if level is None else level
    stats = char.base_stats if stats is None else stats
    rates = char.growth_rates if rates is None else rates
    bvid = char.base_vector_id if bvid is None else bvid
    asset = char.asset if asset is None else asset
    flaw = char.flaw if flaw is None else flaw

    if stat == asset:
        rate = rates[stat] + 5
        stat_increase = 1
    elif stat == flaw:
        rate = rates[stat] - 5
        stat_increase = -1
    else:
        rate = rates[stat]
        stat_increase = 0

    stat_val = stats[stat]

    applied_growth_rate = get_applied_growth_rate(rarity, rate)

    growth_value = get_growth_value(rarity, rate)

    growth_vector_id = get_growth_vector_id(convert_lv1_3star_stats_to_5star(stat_val),
                                            stat, applied_growth_rate, bvid)

    growth_vector = get_growth_vector(growth_value, growth_vector_id)

    # print("{0}: {1}".format(stat, growth_vector))

    stat_increase += rarity_bonuses_for_3_stars(
        get_rarity_bonuses(convert_lv1_3star_stats_to_5star(stats.values())), rarity)[stat]

    # for i in range(level):
    #     stat_increase += int(growth_vector[i])

    stat_increase += sum(map(int, list(growth_vector)[:level]))

    return stat_increase


# def get_stat_increase_for_level_abstract(stat, rarity, level, stats, rates,
#                                          bvid, asset, flaw):
#
#     if stat == asset:
#         rate = rates[stat] + 5
#         stat_increase = 1
#     elif stat == flaw:
#         rate = rates[stat] - 5
#         stat_increase = -1
#     else:
#         rate = rates[stat]
#         stat_increase = 0
#
#     stat_val = stats[stat]
#
#     applied_growth_rate = get_applied_growth_rate(rarity, rate)
#
#     growth_value = get_growth_value(rarity, rate)
#
#     growth_vector_id = get_growth_vector_id(convert_lv1_3star_stats_to_5star(stat_val),
#                                             stat, applied_growth_rate, bvid)
#
#     growth_vector = get_growth_vector(growth_value, growth_vector_id)
#
#     # print("{0}: {1}".format(stat, growth_vector))
#
#     stat_increase += rarity_bonuses_for_3_stars(
#         get_rarity_bonuses(convert_lv1_3star_stats_to_5star(stats.values())), rarity)[stat]
#
#     for i in range(level):
#         stat_increase += int(growth_vector[i])
#
#     # stat_increase = sum(map(int, list(growth_vector)[:level]))
#
#     return stat_increase

def get_stat_increase_for_level(stat, char):
    return get_stat_increase_for_level_abstract_fill(char, stat)


def get_all_stat_increases_for_level(char) -> dict:
    stat_increases = {k: None for k in STAT_dict.values()}

    for stat in STAT_dict.values():
        stat_increases[stat] = get_stat_increase_for_level(stat, char)

    return stat_increases


if __name__ == '__main__':
    class Player:
        def __init__(self, char: dict, rarity, level, asset=None, flaw=None):
            self.rarity = rarity
            self.level = level
            self.base_stats = char["base_stats"]
            self.growth_rates = char["growth_rates"]
            self.base_vector_id = char["base_vector_id"]
            self.asset = asset
            self.flaw = flaw


    char = Player(players_data[0][get_character("Halloween Myrrh", players_data)], 5, 40)

    ups = get_all_stat_increases_for_level(char)

    print(char.base_stats)
    print({k: v + ups[k] for k, v in char.base_stats.items()})
