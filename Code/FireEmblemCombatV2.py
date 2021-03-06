"""
Contains the updated combat logic for FireEmblemClone
"""

from Code.FEH_DijkstraAlgorithm import *
from Code import StatGrowth
from Code.ThreadedLoad_JSON_Data import *
from math import trunc, floor

try:
    from metaproperties import properties, self_properties
except ImportError:
    from Tools.metaproperties import properties, self_properties
from typing import Iterable, Union, Optional, List, Dict, Any, Tuple, NamedTuple, Callable

try:
    from utility_functions import call_with
except:
    from Tools.utility_functions import call_with

# TODO: rework loadfile output dicts to use id_nums tag as keys

# FIXME: change casings
#: Config dictionary
CONFIG = {
    "combat_animations": "off",
    "support_animations": "off",
    "foe/ally autobattle movement": "simple",
    "auto-favorite": "5",
    "starting a map": "go into battle",
    "smart end": "on",
    "show danger area": "off",
    "confirm action": "auto",
    "confirm move": "auto",
    "double tap to wait": "off",
    "auto-battle button": "all locations",
    "assist skills in auto": "no move skills",
    "auto-battle text": "auto-advance",
    "continuous auto": "on",
    "map: no animation": "off",
    "auto: no animation": "off",
    "forging bonds: skip conversation": "off",
    "asset/flaw color display": "on",
    "sorting by level": "default",
    "duo hero display": "full",
    "no duo skill animation": "off",
    "tt difficulty tip": "on",
    "lost lore home notification": "on",
    "mjolnir's strike home notification": "on",  # FIXME: change mjolnir to include diacritics
    "voting gauntlet home notification": "on",
    "forging bonds home notification": "on",
    "compile CMs home notification": "on",
    "AR auto-dispatch home notification": "on",
    "enemy music": "on",
    "battle music": "on",
    "silent mode": "off",
    "BGM volume": 6,
    "SE volume": 5,
    "voice volume": 0,
}

# TODO: rework for compatibility with FEH maps (ex. initialize from map file or dict of tiles)
GRID = Graph.init_as_grid(6, 8)

# ============================================================================================================
# MODULE LEVEL VARIABLE DEFINITIONS START

#: Weapon advantage definitions where 1, 2, and 3 correspond to red, blue, and green, respectively.
#: The value of each key represents the color that has advantage against the key.
weapon_advantage = {
    1: 3,
    2: 1,
    3: 2
}

#: Module-level variable containing all active units
char_list = []

#: Mapping dictionary; maps skill category number to skill type
category_number_to_name_dict = {
    0: "weapon",
    1: "assist",
    2: "special",
    3: "a",
    4: "b",
    5: "c",
    6: "seal",
    7: "refined weapon skill",
    8: "beast transformation"
}

#: Mapping dictionary; maps skill type to skill category number
category_name_to_number_dict = {v: k for k, v in category_number_to_name_dict.items()}

#: Mapping dictionary; maps stat position to stat name
stat_num_to_name_dict = {
    0: "hp",
    1: "atk",
    2: "spd",
    3: "def",
    4: "res"
}


# MODULE LEVEL VARIABLE DEFINITIONS END
# ============================================================================================================


# ============================================================================================================
# CUSTOM EXCEPTIONS DEFINITIONS START

class SkillIsIncorrectCategoryException(Exception):
    """
    Exception raised when a supplied skill is of an incorrect category
    """
    pass


class InvalidWeapon(Exception):
    """
    Exception raised when attempting to equip a weapon a unit does not have access to
    """
    pass


class LimitIdNotFound(Exception):
    pass


# CUSTOM EXCEPTIONS DEFINITIONS END
# ============================================================================================================


# ============================================================================================================
# CLASS DEFINITIONS START

# TODO: Add these to class definitions for positions
class Point(NamedTuple):
    """
    Used to hold character positions
    """
    x: int
    y: int


class ArbitraryAttributeClass:
    """
    Intended for use as a base class to inherit from. Initializes class with attributes
    given by keyword arguments or a supplied dictionary.
    """

    # TODO: Maybe make values be copies? Might be references that cause problems otherwise

    def __init__(self, **kwargs):
        # print(kwargs)
        if "input_dict" in kwargs:
            kwargs.update(kwargs["input_dict"])
            del kwargs["input_dict"]
        if "kwargs" in kwargs:
            kwargs.update(kwargs["kwargs"])
            del kwargs["kwargs"]
        for key in kwargs.keys():
            # print(key, kwargs[key])
            setattr(self, key, kwargs[key])

    @classmethod
    def from_dict(cls, input_dict: dict, **kwargs):
        """
        Builds class from a supplied dictionary and/or list of keyword arguments

        :param input_dict:
        :param kwargs:
        :return: Class with attributes defined by input
        """
        return cls(input_dict=input_dict, kwargs=kwargs)

    def get_all_attrs(self):
        """
        Returns object dictionary

        :return:
        """
        return self.__dict__


# I don't believe this class is necessary
# class Switch:
#     @classmethod
#     def validate_character_attribute(cls, key, value, verbose=False):
#
#         # Create default return function
#         # *args consumes "value" argument
#         def default(input_value):
#             if verbose:
#                 print("Could not validate value {0} as no validation method exists for {0}, "
#                       "defaulting to valid".format(input_value, key))
#
#         # Select validation method
#         method_name = 'validate_' + str(key)
#         # Get the method from 'self'. Defaults to default method.
#         method = getattr(cls, method_name, default)
#         # Call the method and return result, if no
#         output = method(value)
#         if output == 1 or output == 0:
#             return output
#         else:
#             return 1
#
#     @staticmethod
#     def validate_rarity(value):
#         if isinstance(value, int):
#             if 1 <= value <= 5:
#                 return 1
#         elif value is None:
#             return 1
#         return 0
#
#     # TODO: Implement merged and high level unit support
#     @staticmethod
#     def validate_level(value):
#         if isinstance(value, int):
#             if 1 <= value <= 40:
#                 return 1
#         elif value is None:
#             return 1
#         return 0
#
#     @staticmethod
#     def validate_pos(value):
#         grid_size = GRID.get_grid_width_height()
#         if isinstance(value, tuple):
#             if 1 <= value[0] <= grid_size[0] and 1 <= value[1] <= grid_size[1]:
#                 return 1
#         elif value is None:
#             return 1
#         return 0
#
#     @staticmethod
#     def validate_move_range(value):
#         if isinstance(value, int):
#             if 1 <= value <= 3:
#                 return 1
#         elif value is None:
#             return 1
#         return 0
#         pass


class Skill(ArbitraryAttributeClass):
    """
    Class for :class:`Character` skills. Structure defined by JSON data (not dynamically unfortunately,
    I wrote it all by hand).
    """

    def __init__(self, **kwargs):

        #: Full internal string identifier of the skill e.g. SID_ジークリンデ_共 for Sieglinde
        self.id_tag = None
        #: Internal string identifier of the unrefined version of the weapon e.g. SID_ジークリンデ
        self.refine_base = None
        #: Internal string identifier of the skill name resource e.g. MSID_ジークリンデ
        self.name_id = None
        #: Internal string identifier of the skill description resource, e.g. MSID_H_ジークリンデ改
        self.desc_id = None
        #: Internal string identifier of the skill that gives rise to the refined skill effect, e.g. SID_強化共有R
        self.refine_id = None
        #: Internal string identifier of the skill that activates while the unit is transformed into
        #: a beast, e.g. SID_化身効果・奥義強化
        self.beast_effect_id = None
        #: Internal string identifiers of skills required to learn the current skill.
        self.prerequisites = None
        #: Internal string identifier of the canonical upgrade of the current skill. It is defined if and only if
        #: promotion_rarity is not zero.
        self.next_skill = None
        #: Filenames of the sprites used by the weapon, in this order: bow, weapon / arrow, map animation,
        #: AoE Special map animation.
        self.sprites = None

        #: Permanent stat bonuses of the skill. For weapons this does not include might.
        self.stats = None

        #: A set of extra parameters that are used only for skill effects common to weapon classes
        #: for which is_staff, is_dagger, is_breath, or is_beast is true:
        #: - is_staff: If class_params.hp = 1, calculates damage from staff like other weapons.;
        #:   If class_params.hp = 2, foe cannot counterattack.
        #: - is_dagger: After combat, if unit attacked, inflicts stat+class_params on target and foes within
        #:   class_params.hp spaces of target through their next actions.
        #: - is_breath: If class_params.hp = 1, and if target_mov foe uses target_wep, calculates damage
        #:   using the lower of foe's Def or Res.
        #: - is_beast: If class_params.hp = 1, at start of turn, if unit is adjacent to only beast or
        #:   dragon allies or if unit is not adjacent to any ally, unit transforms (otherwise, unit reverts);
        #:   if unit transforms, grants stat+class_params.
        #: .. note::
        #:    is_staff, is_dagger, is_breath, and is_beast are currently implemented as
        #:    Character attributes, not as Weapon attributes or methods
        #:
        self.class_params = None

        #: Various skill parameters packed into a stat tuple. These do not necessarily represent stat values.
        #: Their meanings depend on the skill abilities.
        self.skill_params = None

        #: Various skill parameters packed into a stat tuple. These do not necessarily represent stat values.
        #: Their meanings depend on the skill abilities.
        self.skill_params2 = None

        #: Stat bonuses of the skill's refinement, as shown on the weapon description.
        self.refine_stats = None
        #: A unique increasing index for every skill, added to 0x10000000 for refined weapons.
        self.id_num = None
        #: The internal sort value used in places such as the skill inheritance menu to order skills within
        #: the same category according to their skill families.
        self.sort_id = None
        #: The icon index of the skill, referring to the files UI/Skill_Passive*.png.
        self.icon_id = None
        #: A bitmask indexed by weapon_index, with bits set for weapon classes that can equip the current skill.
        self.wep_equip = None
        #: A bitmask indexed by move_index, with bits set for movement classes that can equip the current skill.
        self.mov_equip = None
        #: SP required to learn the given skill.
        self.sp_cost = None
        #: | Category of the skill.
        #: | 0	0xBC	Weapon
        #: | 1	0xBD	Assist
        #: | 2	0xBE	Special
        #: | 3	0xBF	Passive A
        #: | 4	0xB8	Passive B
        #: | 5	0xB9	Passive C
        #: | 6	0xBA	Sacred Seal
        #: | 7	0xBB	Refined weapon skill effect
        #: | 8	0xB4	Beast transformation effect
        self.category = None

        #: The element type for tome weapon skills.
        self.tome_class = None
        #: True if the skill cannot be inherited.
        self.exclusive = None
        #: True if the skill can only be equipped by enemies.
        self.enemy_only = None
        #: Range of the skill for weapons and Assists, 0 for other skills.
        self.range = None
        #: Might for weapon skills, including bonuses that come from refinements, 0 for other skills.
        self.might = None
        #: Cooldown count of the skill. The total cooldown count of a unit is the sum of cooldown_count
        #: for all equipped skills. Skills that accelerate Special trigger have a negative value.
        self.cooldown_count = None
        #: True if the skill grants Special cooldown count-1 to the unit after this Assist is used.
        self.assist_cd = None
        #: True if the skill is a healing Assist skill.
        self.healing = None
        #:  Range of the skill effect that comes with the given skill, e.g. 1 for Hone skills and
        #:  weapons that give equivalent skill effects.
        self.skill_range = None
        #: A value that roughly corresponds to the SP cost of the skill. Might have been used for Arena matches.
        self.score = None
        #: 2 for a few low-tier Specials and staff weapons / Assists, 0 for highest-tier skills,
        #: and 1 for everything else. Used by derived maps to determine how far skills are allowed to promote.
        self.promotion_tier = None
        #: If non-zero, this skill would be promoted on derived maps if the unit's rarity is greater than or
        #: equal to this value.
        self.promotion_rarity = None
        #: True if the skill is a refined weapon.
        self.refined = None
        #: Internal sort value for refined weapons: 1 and 2 for skills, 101 – 104 for Atk/Spd/Def/Res refinements,
        #: 0 otherwise.
        self.refine_sort_id = None
        #: A bitmask indexed by weapon_index, representing weapon class effectivenesses this skill grants.
        #: Only meaningful on weapon skills.
        self.wep_effective = None
        #: A bitmask indexed by move_index, representing movement class effectivenesses this skill grants.
        #: Only meaningful on weapon skills.
        self.mov_effective = None
        #: A bitmask indexed by weapon_index, representing weapon class effectivenesses this skill protects from.
        #: Used by Breath of Blight.
        self.wep_shield = None
        #: A bitmask indexed by move_index, representing movement class effectivenesses this skill protects from.
        self.mov_shield = None
        #: A bitmask indexed by weapon_index, representing weapon class weaknesses this skill grants.
        #: Used by Loptous.
        self.wep_weakness = None
        #: A bitmask indexed by move_index, representing movement class weaknesses this skill grants.
        #: Currently unused.
        self.mov_weakness = None
        #: A bitmask indexed by weapon_index, representing weapon classes that receive damage from this
        #: skill calculated using the lower of Def or Res. Used by breaths. Only meaningful on weapon skills.
        self.wep_adaptive = None
        #: A bitmask indexed by move_index, representing movement classes that receive damage from this
        #: skill calculated using the lower of Def or Res. Currently unused. Only meaningful on weapon skills.
        self.mov_adaptive = None
        #: An index into the string table in Common/SRPG/SkillTiming.bin indicating the moment where the skill triggers.
        self.timing_id = None
        #: An index into the string table in Common/SRPG/SkillAbility.bin indicating the skill effect type.
        #: A skill can only contain one skill effect (refined weapons have an extra skill effect if
        #: refine_id is non-null).
        self.ability_id = None
        #: An index into the string table in Common/SRPG/SkillTiming.bin indicating the skill's activation restriction.
        self.limit1_id = None
        #: Restriction-dependent parameters.
        self.limit1_params = None
        #: An additional activation restriction on the given skill. Both must be satisfied for the skill to activate.
        self.limit2_id = None
        self.limit2_params = None
        #: A bitmask indexed by weapon_index, representing the target's weapon classes required for the
        #: skill's effect to activate. If zero, works on all weapon classes.
        self.target_wep = None
        #: A bitmask indexed by move_index, representing the target's movement classes required for the
        #: skill's effect to activate. If zero, works on all movement classes.
        self.target_mov = None
        #: Like next_skill, except that this field is null for weapons, Spur Atk 2 does not point to Spur Atk 3,
        #: and similarly for the three other Spur passives.
        #: (Death Blow 3 pointed to Death Blow 4 even before the CYL2 update.)
        self.passive_next = None

        #: A POSIX timestamp relative to the skill's release date; half a month into the future for skills
        #: released before Version 2.0.0, 1 month into the future for skills released since Version 2.0.0.
        #: This skill may be equipped by random units if timestamp is -1 or the current time is past timestamp.
        self.timestamp = None
        #: Indicates whether random units can equip this skill. This affects Training Tower and Allegiance Battles.
        #: It has 3 possible values:
        #: - 0: This skill may not be equipped on random units.
        #: - 10: This skill may be equipped on random units.
        #: - 20: Purpose unknown. Same effect as 10. Used by basic non-staff weapons
        #:   (e.g. Iron Sword, Flametongue+, Adult (Cavalry)) and basic staff Assists.
        self.random_allowed = None
        #: If non-zero, represent the lowest and highest levels respectively that allow random units
        #: to equip the given skill.
        self.min_lv = None
        self.max_lv = None
        #: If true, this skill may be considered by the 10th Stratum of the Training Tower for the
        #: random skill pool if it is equipped by the corresponding unit from the base map.
        self.tt_inherit_base = None
        #: Controls how random units may equip this skill. It has 3 possible values: (see #Random skills for details)
        #:   - 0: This skill may not be equipped on random units.
        #:   - 1: This skill may be equipped by any random unit.
        #:   - 2: This skill may be equipped by random units that own the skill.
        self.random_mode = None

        #: Defines the shape used for range functions (finding units within range of skill).
        #: Shape refers to the physical shape, such as column, row, cardinals, etc.
        self.range_shape = None

        #: Controls whether skill targets units with both the targeted weapon *and* targeted
        #: movement type or whether having either one marks the unit as a valid target
        self.target_either = None

        # Unknown usage
        # self.id_tag2 = id_tag2
        # self.next_seal = next_seal
        # self.prev_seal = prev_seal
        # self.ss_coin = ss_coin
        # self.ss_badge_type = ss_badge_type
        # self.ss_badge = ss_badge
        # self.ss_great_badge = ss_great_badge

        super().__init__(**kwargs)

    def activate(self, **kwargs):

        # gets first limit function
        if self.limit1_id != 0:
            limit1 = getattr(eval(f"stid{self.timing_id}"), f"slid{self.limit1_id}")
        else:
            # if the limit id is 0, there is no limit
            limit1 = lambda **kwargs: True

        # gets second limit function
        if self.limit2_id != 0:
            limit2 = getattr(eval(f"stid{self.timing_id}"), f"slid{self.limit2_id}")
        else:
            # if the limit id is 0, there is no limit
            limit2 = lambda **kwargs: True

        # print(self.limit1_id, self.limit2_id)

        # gets the ability function
        ability = getattr(eval(f"stid{self.timing_id}"), f"said{self.ability_id}")

        char = kwargs["unit"]

        # tests whether the ability activates for each character
        # if so, activates ability with that character as the target
        # for char in char_list:
        # print(f"    {char}: {(limit1(skill=self, target=char), limit2(skill=self, target=char))}")
        if limit1(skill=self, target=char) and limit2(skill=self, target=char):
            # print(f"Calling for {char}")
            call_with(ability, dict(kwargs, unit=char, target=char))

    def targeted(self, items: Iterable['Character']):
        """
        Return list of units within the given group which are targeted by the skill. Skill targeting
        is defined by the skill's target_mov and target_wep attributes.

        :param items:
        :return:
        """

        return [i for i in items if self.skill_targets(i)]

    def skill_targets(self, unit: 'Character'):
        """
        Similar to :meth:`targeted` method. Return boolean value based on whether given unit is
        targeted by skill. Skill targeting is defined by the skill's target_mov and
        target_wep attributes.

        :param unit: :class:`Character`
        :return: bool
        """
        # print("Unit move type:", unit.move_type, "\nTarget move type:", self.target_mov,
        #       "\nUnit weapon type:", unit.weapon_type, "\nTarget weapon type:", self.target_wep)

        targets_mov = in_bitmask(unit.move_type, self.target_mov) or self.target_mov == 0
        targets_wep = in_bitmask(unit.weapon_type, self.target_wep) or self.target_wep == 0

        # print(f"        targets_mov: {targets_mov}; targets_wep: {targets_wep}")

        if self.target_either:
            return True if targets_mov or targets_wep else False
        else:
            return True if targets_mov and targets_wep else False

        # if self.target_either:
        #     return True if unit.move_type == self.target_mov or \
        #                    unit.weapon_type == self.target_wep else False
        # else:
        #     return True if unit.move_type == self.target_mov and \
        #                    unit.weapon_type == self.target_wep else False

    def combat_boost(self, unit: 'Character'):
        """
        For each stat, grants/inflicts skill's ``stat`` + skill's ``skill_params``
        to/on ``unit`` during combat.

        :param unit: :class:`Character`
        :return: None
        """
        for stat, stat_value in self.stats:
            unit.combat_boosts[stat] += stat_value + self.skill_params[stat]

    def combat_boost2(self, unit: 'Character'):
        """
        For each stat, grants/inflicts skill's ``stat`` + skill's ``skill_params2``
        to/on ``unit`` during combat.

        :param unit: :class:`Character`
        :return: None
        """
        for stat, stat_value in self.stats:
            unit.combat_boosts[stat] += stat_value + self.skill_params[stat]


class WeaponClass(ArbitraryAttributeClass):
    """
    This class refers to a weapon's base weapon-class. For example, the base weapon
    class of Clarisse's Sniper's Bow is colorless bow

    .. warning::
       Not to be confused with the :class:`Weapon` class
    """

    def __init__(self, **kwargs):
        #: Internal identifier tag
        self.id_tag = None
        self.sprite_base = None
        #: Base weapon of this class (ex. Iron Sword for Sword weapon class)
        self.base_weapon = None
        self.index = None
        self.color = None
        #: int: Weapon class range (melee or ranged)
        self.range = None
        self._unknown1 = None
        self.sort_id = None
        self.equip_group = None
        #: bool: Does weapon class use res to calculate damage
        self.res_damage = None
        #: bool
        self.is_staff = None
        #: bool
        self.is_dagger = None
        #: bool
        self.is_breath = None
        #: bool
        self.is_beast = None

        super().__init__(**kwargs)


class Weapon(Skill):
    def __init__(self, **kwargs):

        #: :class:`WeaponClass`: Base weapon class
        self.weapon_class = None

        super().__init__(**kwargs)
        # self.set_attribute_values()

    def set_attribute_values(self):
        """
        Calls :meth:`get_base_weapon_class` if weapon does not already have a :class:`WeaponClass`

        :return: None
        """
        if not self.weapon_class:
            self.weapon_class = self.get_base_weapon_class(self)

    @staticmethod
    def get_base_weapon_class(weapon):
        weapon_data_by_base_weapon_id = {v["base_weapon"]: v for v in weapons_data[1].values()}

        # FIXME: This can probably be combined and made more compact
        prereqs = list(filter(lambda pr: pr is not None, weapon.prerequisites))
        if len(prereqs) == 0:
            if weapon.id_tag in weapon_data_by_base_weapon_id:
                # do stuff in weapon.json
                base_weapon_class = weapon_data_by_base_weapon_id[weapon.id_tag]
            else:
                bin_list = list(map(int, list(bin(weapon.mov_equip)[2:])))
                base_weapon_class = weapon_data_by_index[len(bin_list) - 1 - bin_list.index(1)]

        else:
            prereq = prereqs[0]
            while True:
                prereqs = list(filter(lambda pr: pr is not None, skills_data[1][prereq]["prerequisites"]))
                if len(prereqs) == 0:
                    base_weapon_class = weapon_data_by_base_weapon_id[prereq]
                    break
                else:
                    prereq = prereqs[0]
        return WeaponClass.from_dict(base_weapon_class)


class Character(ArbitraryAttributeClass):

    # __slots__ = ['id_tag', 'roman', 'face_name', 'face_name2', 'legendary', 'dragonflowers',
    #              'timestamp', 'id_num', 'sort_value', 'origins', 'weapon_type', 'tome_class',
    #              'move_type', 'series', 'regular_hero', 'permanent_hero', 'base_vector_id',
    #              'refresher', 'base_stats', 'growth_rates', 'skills', 'pos', 'node', 'move_range',
    #              'rarity', 'level', 'affinity', 'weapon', 'weapon_class', 'color', 'name',
    #              'equipped_skills', 'stats', 'buffs', 'debuffs', 'combat_boosts', 'counter',
    #              'no_counter', 'follow_up', 'vantage', 'desperation', 'brave', 'raven', 'adaptive',
    #              'adaptive_aoe', 'wrathful_staff', 'status_effects', 'is_initiating', 'special_cd',
    #              'max_special_cd', 'has_acted', '_id_tag', '_roman', '_face_name', '_face_name2',
    #              '_legendary', '_dragonflowers', '_timestamp', '_id_num', '_sort_value', '_origins',
    #              '_weapon_type', '_tome_class', '_move_type', '_series', '_regular_hero',
    #              '_permanent_hero', '_base_vector_id', '_refresher', '_base_stats', '_growth_rates',
    #              '_skills', '_pos', '_node', '_move_range', '_rarity', '_level', '_affinity',
    #              '_weapon', '_weapon_class', '_color', '_name', '_equipped_skills', '_stats',
    #              '_buffs', '_debuffs', '_combat_boosts', '_counter', '_no_counter', '_follow_up',
    #              '_vantage', '_desperation', '_brave', '_raven', '_adaptive', '_adaptive_aoe',
    #              '_wrathful_staff', '_status_effects', '_is_initiating', '_special_cd',
    #              '_max_special_cd', '_has_acted', '_hp', ]

    def __init__(self, **kwargs):

        #: internal identifier tag
        self.id_tag = None
        self.id_tag: str
        #: romanized name
        self.roman = None
        self.roman: str
        #: stores reference to face file
        self.face_name = None
        self.face_name2 = None
        self.face_name: str
        self.face_name2: str
        #: character legendary status
        self.legendary = None
        self.legendary: Dict
        #: number of dragon flowers added
        self.dragonflowers = None
        self.dragonflowers: Dict
        #: release date
        self.timestamp = None
        self.timestamp: str
        # internal identifier number (higher the more recent a unit is)
        self.id_num = None
        self.id_num: int
        #: sort priority (bitmask?)
        self.sort_value = None
        self.sort_value: int
        #
        self.origins = None
        #: weapon type; integer
        self.weapon_type = None
        self.weapon_type: int
        #: tome's magic type; 0 for non-magic characters
        self.tome_class = None
        self.tome_class: int
        #: movement type (flier, infantry, armor, cavalry)
        self.move_type = None
        self.move_type: int
        #
        self.series = None
        #
        self.regular_hero = None
        self.regular_hero: bool
        #
        self.permanent_hero = None
        self.permanent_hero: bool
        #: value used to construct stat growth vectors
        self.base_vector_id = None
        self.base_vector_id: int
        #: dancer/singer status; boolean
        self.refresher = None
        self.refresher: bool
        #: base stat values at 3 star rarity, level 1
        self.base_stats = None
        self.base_stats: Dict[str, int]
        #: percent growth rates for each stat
        self.growth_rates = None
        self.growth_rates = Dict[str, int]
        #: List of lists: index of first list corresponds to unit rarity; index of second list
        #: corresponds to skill category.
        #: For given rarity, first 6 values (0-5) are default (already learned), remaining 8 (6-13)
        #: are unlockable
        #: - index 0 and index 6 are weapons
        #: - index 1 and index 7 are assists
        #: - index 2 and index 8 are specials
        #: - index 3 and index 9 are A slot (except for Drag Back on Gwendolyn)
        #: - index 4 and index 10 are B slot (Except Defiant Attack on Ogma)
        #: - index 5 and index 11 are C slot (Except HP+ on Abel)
        #: - index 12 is empty
        #: - index 13 is empty
        self.skills = None
        self.skills: List[List]

        #: position; tuple (x, y)
        self.pos = None
        self.pos = Tuple[int, int]
        #: node at character's position
        self.node = None
        self.node: Node
        #: movement range; integer
        self.move_range = None
        self.move_range: int
        #: current rarity; integer
        self.rarity = None
        self.rarity: int
        #: current level; integer
        self.level = None
        self.level: int
        #: affinity bonus (bonus granted by skills like gem weapons or triangle adept)
        self.affinity = None
        #: currently equipped weapon
        self.weapon: Union[Weapon, None] = None
        #: base weapon class (kinda useless right now?)
        self.weapon_class = None
        #: unit color; integer
        self.color = None
        self.color: int
        #: translated unit name
        self.name = None
        self.name: str
        #: Currently equipped skills. Dict keys correspond to skill category.
        self.equipped_skills = None
        self.equipped_skills: Dict[str, Skill]
        #: stats scaled to current level
        self.stats = None
        self.stats: Dict[str, int]
        #: visible buffs applied to unit; integer
        self.buffs = None
        self.buffs: Dict[str, int]
        #: visible debuffs applied to unit; integer
        self.debuffs = None
        self.debuffs: Dict[str, int]
        #: sum of invisible in-combat buffs/debuffs applied to unit; integer
        self.combat_boosts = None
        self.combat_boosts: Dict[str, int]
        #: current hp value; integer
        self._hp = None
        self._hp: int
        #: unit can counterattack regardless of opponent’s range; boolean
        self.counter = None
        self.counter: bool
        #: unit cannot counterattack; boolean
        self.no_counter = None
        self.no_counter: bool
        #: can unit make a follow-up (1 = guaranteed, 0 = normal, -1 = no follow-up); integer
        self.follow_up = None
        self.follow_up: int
        #: does unit have vantage; boolean
        self.vantage = None
        self.vantage: bool
        #: does unit have desperation; boolean
        self.desperation = None
        self.desperation: bool
        #: does unit have brave effect; boolean
        self.brave = None
        self.brave: bool
        #: does unit have raven effect; boolean
        self.raven = None
        self.raven: bool
        #: does unit have adaptive damage; boolean
        self.adaptive = None
        self.adaptive: bool
        #: does unit have adaptive special damage; boolean
        self.adaptive_aoe = None
        self.adaptive_aoe: bool
        #: does unit calculate damage from staff like normal weapons; boolean
        self.wrathful_staff = None
        self.wrathful_staff: bool
        #: dictionary of status effects on unit; string keys and boolean values
        self.status_effects = None
        self.status_effects: Dict[str, bool]
        #: is unit the one initiating combat; boolean
        self.is_initiating = None
        self.is_initiating: bool
        # TODO: Make equipping a special skill affect this value
        #: Current special cooldown value; int
        self.special_cd = None
        self.special_cd: int
        #: Maximum special cooldown value; int
        self.max_special_cd = None
        self.max_special_cd: int
        #: has unit acted already; boolean
        self.has_acted = None
        self.has_acted: bool
        #: Unit's asset stat
        self.asset = None
        self.asset: Union[None, str]
        #: Unit's flaw stat
        self.flaw = None
        self.flaw: Union[None, str]

        super().__init__(**kwargs)
        # scope = self.__dict__.copy()
        #
        # # print("Self scope:", scope)
        # self_properties(self, scope)

        self.set_attribute_values()

        # print("Self dir:", dir(self))
        # print("Self __dict__:", self.__dict__)
        # print("Self __slots__:", self.__slots__)

        char_list.append(self)

    # def __setattr__(self, key, value):
    #
    #     if Switch.validate_character_attribute(key, value):
    #         super().__setattr__(key, value)
    #     else:
    #         raise ValueError("Invalid value supplied for {0} attribute of {1}".format(key, self))

    def __repr__(self):
        return "{0}, {1} ({2} object with id {3})".format(self.id_tag, self.roman, self.__class__, id(self))

    with properties(locals(), 'meta') as meta:
        @meta.prop(listener='hp_change')
        def hp(self):
            """hp"""
            return self._hp

    def hp_change(self, prop, old, new):
        """
        Listener function for changes in a :class:`Character`'s hp. Checks whether hp change resulted
        in death.

        :param prop:
        :param old:
        :param new:
        :return:
        """
        self.check_is_dead()

    def set_attribute_values(self):
        """
        Sets default values for character attributes

        :return:
        """

        # if character's position is defined, sets "node" attribute to a Node object in the map grid and
        # sets node's "holds" attribute to character
        if self.pos:
            self.node = GRID.nodes[GRID.get_index_from_xy(self.pos)]
            self.node.holds = self

        # for all attributes below, checks whether attribute is already set, and if not, sets to
        # default value; sets movement range based on movement type
        if not self.move_range:
            self.move_range = move_data[self.move_type]["range"]
        # sets rarity to 3 stars by default
        if not self.rarity:
            self.rarity = 3
        # sets character level to 1
        if not self.level:
            self.level = 1
        # sets affinity bonus to 0
        if not self.affinity:
            self.affinity = 0
        # sets stats to base stats for current level
        # TODO: Add support for IVs
        if not self.stats:
            print(self)
            # self.stats = self.base_stats
            self.stats = {}
            self.set_stats_to_stats_for_level()
        # sets current buffs to 0
        if not self.buffs:
            self.buffs = {
                "atk": 0,
                "spd": 0,
                "def": 0,
                "res": 0
            }
        if not self.debuffs:
            self.debuffs = {
                "atk": 0,
                "spd": 0,
                "def": 0,
                "res": 0
            }
        # sets current in-combat buffs/debuffs sum to 0
        if not self.combat_boosts:
            self.combat_boosts = {
                "atk": 0,
                "spd": 0,
                "def": 0,
                "res": 0
            }
        # sets current hp to base hp value for current level
        if not self.hp:
            self.hp = self.stats["hp"]
        # sets color based on weapon type
        if not self.color:
            self.color = weapon_index_to_color_dict[self.weapon_type]
        # sets weapon class based on weapon type (not needed?)
        if not self.weapon_class:
            self.weapon_class = WeaponClass.from_dict(weapon_data_by_index[self.weapon_type])

        # equips weapon to unit; defaults to None (recently added id_tag part, check it)
        self.equip_weapon(weapon=self.weapon)

        # sets character's name
        if not self.name:
            self.name = str(translate_jp_to_en_dict(self.__dict__, english_data,
                                                    prefix="MPID", old_prefix="PID"))

        # sets character's equipped skill for each category to None
        if not self.equipped_skills:
            self.equipped_skills = {

                "assist": None,
                "special": None,
                "a": None,
                "b": None,
                "c": None,
                "seal": None
            }

    def check_is_dead(self):
        if self.hp <= 0:
            self.die()
            return 1
        return 0

    def validate_skill(self, skill: Skill):
        # checks if character is of correct weapon type and move type
        if in_bitmask(self.weapon_type, skill.wep_equip) and in_bitmask(self.move_type, skill.mov_equip):

            if skill.exclusive:
                # checks if character owns exclusive skill
                owns_skill = False
                for skillset in self.skills:
                    if skill.id_tag in skillset:
                        owns_skill = True
                        break
                if not owns_skill:
                    return False

            if skill.enemy_only:
                # checks if character is an enemy
                if not (self.__class__ == Enemy or self.id_tag.startswith("EID_")):
                    return False

            if skill.healing:
                # checks if character is a staff unit
                if self.weapon_type != 15:
                    return False

            return True

        return False
        pass

    def get_skill(self, category: str):
        skill = None
        category = category_name_to_number_dict[category]
        for i in range(self.rarity):
            skill = self.skills[i][category] if self.skills[i][category] is not None else skill
        if skills_data[1][skill]["category"] == category:
            return Skill.from_dict(skills_data[1][skill])
        else:
            raise SkillIsIncorrectCategoryException(
                "Skill should be a category {0} skill, received category {1} skill instead".format(category, str(
                    skills_data[1][skill]["category"]))
            )
        pass

    # handles equipping a skill to a character
    def equip_skill(self, skill: str):
        if skill is not None:
            # create Skill object from weapon id
            skill = Skill.from_dict(skills_data[1][skill])
            # check whether character can equip skill
            if self.validate_skill(skill):

                category = category_number_to_name_dict[skill.category]

                # if character already has a weapon equipped, unequip it
                if self.equipped_skills[category]:
                    self.unequip_skill(category)

                # # add weapon's might to character's attack stat
                # self.stats["atk"] += weapon.might

                # add skill's stat bonuses to character's stats
                for stat in skill.stats:
                    self.stats[stat] += skill.stats[stat]
                self.hp += skill.stats["hp"]

                # update character's equipped_skills attribute with skill
                self.equipped_skills[category] = skill

            else:
                # if skill fails to pass validation, character cannot equip skill
                raise InvalidWeapon("Character {0} does not have access to skill {1}".format(self, skill.id_tag))

    # handles unequipping a skill from a character
    def unequip_skill(self, category: str):
        skill = self.equipped_skills[category]
        if skill is not None:
            if isinstance(skill, Skill):
                for stat in skill.stats:
                    self.stats[stat] -= skill.stats[stat]
                # TODO: Create getter/setter for self.stats to auto-modify self.hp
                self.hp -= skill.stats["hp"]

            self.equipped_skills[category] = None
        pass

    # TODO: Add in support for automatic skill/weapon generation for TT and the like
    def validate_weapon(self, weapon: Weapon):
        """
        Checks whether unit may possess weapon

        :type weapon: Weapon
        """

        # checks if character is of correct weapon type and move type
        if in_bitmask(self.weapon_type, weapon.wep_equip) and in_bitmask(self.move_type, weapon.mov_equip):

            # FIXME: Does not currently support refined weapons
            # Idea for refined weapons: check num of underscores, greater than 1, remove suffix and check base
            if weapon.exclusive:
                # checks if character owns exclusive weapon
                owns_weapon = False
                for skillset in self.skills:
                    if weapon.id_tag in skillset:
                        owns_weapon = True
                        break
                if not owns_weapon:
                    print("Does not own weapon")
                    return False

            if weapon.enemy_only:
                # checks if character is an enemy
                if not (self.__class__ == Enemy or self.id_tag.startswith("EID_")):
                    return False

            return True

        return False

    def get_weapon(self):
        weapon = None
        for i in range(self.rarity):
            weapon = self.skills[i][0] if self.skills[i][0] is not None else weapon
        if skills_data[1][weapon]["category"] == 0:
            return Weapon.from_dict(skills_data[1][weapon])
        else:
            raise SkillIsIncorrectCategoryException(str("Weapon should be a category 0 skill, received category " + str(
                skills_data[1][weapon]["category"]) + " skill instead"))
        pass

    def equip_weapon(self, weapon: Union[str, Weapon]):
        """
        Handles equipping a weapon to a character

        :param weapon:
        :return:
        """
        if weapon is not None:

            if isinstance(weapon, str):
                # create weapon object from weapon id
                weapon = Weapon.from_dict(skills_data[1][weapon])

            # check whether character can equip weapon
            if self.validate_weapon(weapon):

                # if character already has a weapon equipped, unequip it
                if self.weapon:
                    self.unequip_weapon()

                # add weapon's might to character's attack stat
                self.stats["atk"] += weapon.might

                # add weapon's stat bonuses to character's stats (separate from might)
                for stat in weapon.stats:
                    self.stats[stat] += weapon.stats[stat]
                self.hp += weapon.stats["hp"]

                # set character's weapon attribute to weapon
                self.weapon = weapon

            else:
                # if weapon fails to pass validation, character cannot equip weapon
                raise InvalidWeapon("Character {0} does not have access to weapon {1}".format(self, weapon.id_tag))

        # if weapon to equip is None, unequip weapon
        else:
            self.unequip_weapon()

    def unequip_weapon(self):
        """
        Handles unequipping a weapon

        :return:
        """
        if self.weapon is not None:
            if isinstance(self.weapon, Weapon):
                self.stats["atk"] -= self.weapon.might

                for stat in self.weapon.stats:
                    self.stats[stat] -= self.weapon.stats[stat]
                self.hp -= self.weapon.stats["hp"]

            self.weapon = None

    def get_distance_to(self, enemy: "Character"):
        """
        Returns distance from unit to `enemy`

        :param enemy:
        :return:
        """
        return get_distance(self, enemy)

    def calc_weapon_triangle(self, enemy: "Character"):
        """
        Checks whether unit has weapon advantage/disadvantage against `enemy` and returns
        corresponding attack multiplier value as a percent (i.e., 0.2, -0.2, or 0)

        :param enemy:
        :return:
        """

        # if character has weapon triangle advantage, increase attack by 20%
        if enemy.color == weapon_advantage[self.color]:
            return 0.2
        # if character has weapon triangle disadvantage, decrease attack by 20%
        elif self.color == weapon_advantage[enemy.color]:
            return -0.2
        # if character has neither weapon triangle advantage or disadvantage, do not modify attack
        # if either character or enemy is colorless, weapon triangle does not apply
        # FIXME: Add support for raven-tomes and weapon triangle advantage against colorless
        elif self.color == enemy.color or self.color == "gray" or enemy.color == "gray":
            return 0

    def calc_effectiveness(self, enemy: "Character"):
        """
        Checks whether unit has weapon effectiveness against `enemy` and returns
        corresponding attack multiplier value (i.e., 1.5 or 1)

        :param enemy:
        :return:
        """
        # assertions used to force IDE autocompletion
        assert isinstance(enemy.weapon, Weapon)
        assert isinstance(self.weapon, Weapon)

        # bitmask of movement types unit has effectiveness against
        mov_effective = self.weapon.mov_effective
        # bitmask of weapon types unit has effectiveness against
        wep_effective = self.weapon.wep_effective

        # if unit is effective against enemy movement type or enemy has movement weakness,
        # and enemy does not have a movement shield effect, then deal 50% extra damage
        if (in_bitmask(enemy.move_type, mov_effective)
            or in_bitmask(enemy.weapon.mov_weakness, mov_effective)) \
                and not in_bitmask(enemy.weapon.mov_shield, mov_effective):
            return 1.5

        # if unit is effective against enemy weapon type or enemy has weapon weakness,
        # and enemy does not have a weapon shield effect, then deal 50% extra damage
        if (in_bitmask(enemy.weapon_type, wep_effective)
            or in_bitmask(enemy.weapon.wep_weakness, wep_effective)) \
                and not in_bitmask(enemy.weapon.wep_shield, wep_effective):
            return 1.5

        # otherwise, deal normal damage
        return 1

    def calc_boosted_damage(self, enemy: "Character"):
        return 0
        # TODO: add functionality

    def set_stats_to_stats_for_level(self):
        """
        Gets stats for unit at current level and sets stats to corresponding values

        :return: None
        """
        stat_increases = StatGrowth.get_all_stat_increases_for_level(self)
        for stat in stat_increases:
            self.stats[stat] = self.base_stats[stat] + stat_increases[stat]

    def damage_enemy(self, enemy: 'Character', damage: int):
        enemy.hp -= damage
        # add on_damage effects here

    def attack_enemy(self, enemy: "Character"):
        """
        Handles attacking an `enemy`

        :param enemy:
        :return: None
        """
        assert isinstance(self.weapon, Weapon)
        assert isinstance(enemy.weapon, Weapon)

        if enemy.pos == self.pos:
            print("You can't attack yourself silly")
            return None
        if enemy.hp > 0:
            if self.get_distance_to(enemy) == self.weapon.range:
                print("Enemy in range, commencing attack")

                # TODO: Create function for this
                atk = self.stats["atk"] + self.buffs["atk"] + self.combat_boosts["atk"]

                # TODO: Add support for adaptive damage
                # self.weapon.tome_class
                mit_stat = "def" if self.tome_class == 0 else "res"
                mitigation = enemy.stats[mit_stat] + enemy.buffs[mit_stat] + enemy.combat_boosts[mit_stat]

                damage = pos(floor(atk * self.calc_effectiveness(enemy)) + trunc(
                    floor(atk * self.calc_effectiveness(enemy)) * (self.calc_weapon_triangle(enemy) * (
                            self.affinity + 20) / 20)) + self.calc_boosted_damage(enemy) - mitigation)

                self.damage_enemy(enemy, damage)

                if enemy.hp > 0:
                    print(self.name, "dealt", damage, "damage,", enemy.name, "has", enemy.hp, "HP remaining")
                else:
                    print(self.name, "dealt", damage, "damage,", enemy.name, "has been defeated")
                    # enemy.die()

                return None
            print("Enemy not in range")
        else:
            print("Enemy has already been defeated")

    def attack_node(self, pos: Tuple[int, int]):
        """
        Attacks a designated node using :meth:`attack_enemy`

        :param node:
        :return: None
        """
        enemy = GRID.nodes[GRID.get_index_from_xy(pos)].holds
        if enemy is not None:
            self.attack_enemy(enemy)
        else:
            print("There is no enemy at position", pos)

    def move(self, new_pos: tuple):
        """
        Handles character movement

        :param new_pos:
        :return: None
        """
        print(self.name, "moved", get_distance_from_tuples(self.pos, new_pos), "spaces from", self.pos, "to", new_pos)
        GRID.nodes[GRID.get_index_from_xy(self.pos)].holds = None
        self.pos = new_pos
        GRID.nodes[GRID.get_index_from_xy(new_pos)].holds = self

    def fight(self, enemy: "Character"):
        """
        Handles a fight between unit and `enemy`. Uses :meth:`attack_enemy` for both sides and
        calculates whether either side doubles.

        :param enemy:
        :return: None
        """
        self.is_initiating = True
        # TODO: Add check for vantage skill
        self.attack_enemy(enemy)
        # is this check necessary? Already checks in attack_enemy function
        if enemy.hp > 0:
            # TODO: Add checks for "prevent counterattack" status, weapon range, distant/close counter skills
            # TODO: Add check for desperation skill
            enemy.attack_enemy(self)
            # FIXME: Apply buffs/debuffs
            if self.stats["spd"] >= enemy.stats["spd"] + 5 and self.stats["hp"] > 0:
                self.attack_enemy(enemy)
            elif enemy.stats["spd"] >= self.stats["spd"] + 5:
                enemy.attack_enemy(self)

        # Do after-combat checks
        self.is_initiating = False

    def move_to_attack(self, enemy: "Character"):
        """
        Intended for use by AI (or lazy players I guess). Moves unit using :meth:`move_towards` and
        then attacks `enemy` using :meth:`fight`

        :param enemy:
        :return: None
        """
        endpoints = GRID.dijkstra(enemy.pos, eval_to_length=self.weapon.range)

        endpoints = [i for i in [points[-1] if get_distance_from_tuples(enemy.pos, points[-1].data) ==
                                               self.weapon.range else None for (weight, points) in endpoints] if
                     i is not None]

        endpoints = [endpoint for endpoint in endpoints if
                     get_distance_from_tuples(self.pos, endpoint.data) <= self.move_range]

        if len(endpoints) == 0:
            print("No available moves that can target", enemy.name)
        else:
            endpoint = endpoints[0]
            print("Chose position", endpoint.data, "from possible positions", [endpoint.data for endpoint in endpoints])

            if endpoint.data == self.pos:
                print(self.name, "stays where they are and attacks", enemy.name, "at position", enemy.pos)
            else:
                print(self.name, "moves to", endpoint.data, "to attack", enemy.name, "at position", enemy.pos)
                self.move(endpoint.data)

            self.fight(enemy)

    def move_towards(self, enemy: "Character"):
        """
        Utilizes dijkstra algorithm to find valid spaces from which unit can attack `enemy`
        and moves unit to closest.

        :param enemy:
        :return: None
        """
        weight, nodes = GRID.dijkstra(self.pos, enemy.pos, only_end=True)[0]

        distance = get_distance_from_tuples(self.pos, enemy.pos)

        if distance == self.weapon.range:
            print(self.name, "is already in range and does not move")

        if distance > self.weapon.range:
            move_distance = distance - self.weapon.range
            if move_distance > self.move_range:
                self.move(nodes[self.move_range].data)
            else:
                self.move(nodes[move_distance].data)
            pass

        if distance < self.weapon.range:
            print(self.name, "is too close and moves further away")

    def move_direction(self, direction: Tuple, distance: int = 1):
        """
        Moves unit in the specified direction.

        :param direction: X,Y tuple specifying the individual distances to move in the
        X and Y directions
        :param distance: Integer value by which direction tuple is scaled. Defaults to one.
        :return: None
        """

        self.move(tuple_add(self.pos, scale_tuple(direction, distance)))

    def die(self):
        """
        Handles unit death. Removes unit from the field and :data:`char_list`.

        :return:
        """
        if self.pos:
            GRID.nodes[GRID.get_index_from_xy(self.pos)].holds = None
        char_list.remove(self)

    def stat(self, stat_num):
        """
        Takes in number between 0 and 4 and translates to corresponding stat, then returns
        unit's value for this stat.

        :param stat_num: Integer between 0 and 4
        :return:
        """
        return self.stats[stat_num_to_name_dict[stat_num]]

    def stat2(self, stat_num):
        """
        Takes in number between 0 and 4 and translates to corresponding stat, then returns sum of
        unit's value for this stat and this stat's current buff.

        :param stat_num: Integer between 0 and 4
        :return:
        """
        stat_name = stat_num_to_name_dict[stat_num]
        return self.stats[stat_name] + self.buffs[stat_name]

    def stat_difference(self, stat_num, other: "Character"):
        """
        Returns difference between given stat for unit and `other` unit.

        :param stat_num: Integer between 0 and 4
        :param other:
        :return:
        """
        # TODO: Include phantom skills in calculation
        # CHECK: Should I wrap this in abs()?
        return self.stat(stat_num) - other.stat(stat_num)
        pass


class Enemy(Character):
    """
    Enemy class. Defines behaviors and characteristics for enemy units.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Player(Character):
    """
    Player class. Defines behaviors and characteristics for player units.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# CLASS DEFINITIONS END
# ============================================================================================================

# ============================================================================================================
# GENERAL DEFINITIONS START

def tuple_add(tup1, tup2):
    """
    Simple utility function that adds 2 (X,Y) tuples and returns the result.

    :param tup1:
    :param tup2:
    :return:
    """
    return (tup1[0] + tup2[0], tup1[1] + tup2[1])


def scale_tuple(tup, scale):
    """
    Simple utility function that scales an (X,Y) tuple by an integer value and returns the result.

    :param tup:
    :param scale:
    :return:
    """
    return (tup[0] * scale, tup[1] * scale)


def get_distance_from_tuples(self: tuple, enemy: tuple):
    """
    Simple utility function that returns the distance between 2 (X,Y) tuples. Distance is not the
    minimal diagonal distance as given by the standard distance function, but rather the tile-based
    distance used to navigate grids. For example, if an object A is at position (1,1) and an object B
    is at position (3,4), the distance is 5 (as opposed to the shortest-route diagonal distance of
    3.60555...)

    :param self:
    :param enemy:
    :return:
    """
    return abs(enemy[0] - self[0]) + abs(enemy[1] - self[1])


def get_distance(self: Character, enemy: Character):
    """
    Simple utility function that returns the distance between 2 (X,Y) :class:`Character` units.
    Uses the same logic as in :func:`get_distance_from_tuples`.

    :param self:
    :param enemy:
    :return:
    """
    return abs(enemy.pos[0] - self.pos[0]) + abs(enemy.pos[1] - self.pos[1])


def convert_to_bitmask_list(int_bitmask: int) -> list:
    """
    Converts integer bitmask to list of 1's and 0's, e.g if 'int_bitmask' is 571,
    returns [1, 1, 0, 1, 1, 1, 0, 0, 0, 1]

    :param int_bitmask:
    :return:
    """
    return list(map(int, list(bin(int_bitmask)[::-1][:-2])))


def filter_true_indexes(bitmask_list: List[int]) -> List[int]:
    """
    Takes a bitmask list 'bitmask_list' (output from convert_to_bitmask_list function) and returns a list
    of integers for each index in 'bitmask_list' at which the value is True (or in this case, 1)

    :param bitmask_list:
    :return:
    """
    return [i for i, v in enumerate(bitmask_list) if v]


def in_bitmask(nums: Union[int, Iterable[int]], bitmask: int) -> Union[bool, Dict[int, Any]]:
    """
    Takes an integer bitmask 'bitmask', converts to binary, and casts binary to a list of ones and
    zeroes, 'bitmask_list'.

    If 'nums' is an integer:
         Indexes 'bitmask_list' by 'nums', if value at index is 1 returns True, else False

    If 'nums' is an Iterable of integers:
        For 'num' in 'nums', indexes 'bitmask_list' by 'num', if value at index is 1 sets value to True
        at key 'num' in 'in_bitmask_dict' else sets value to False

    :param nums:
    :param bitmask:
    :return:
    """

    bitmask_list = convert_to_bitmask_list(bitmask)

    in_bitmask_dict = dict()

    if isinstance(nums, int):
        # print("Bitmask:", bitmask)
        # print("Bitmask_list:", bitmask_list)
        # print("Nums:", nums)
        # if len(bitmask_list) < nums:
        if len(bitmask_list) <= nums:
            return False
        return True if bitmask_list[nums] == 1 else False

    # filtered = filter_true_indexes(bitmask_list)
    # for num in nums:
    #     if num in filtered:
    #         in_bitmask_dict[num] = True
    #     else:
    #         in_bitmask_dict[num] = False

    for num in nums:
        try:
            if bitmask_list[num] == 1:
                in_bitmask_dict[num] = True
            else:
                in_bitmask_dict[num] = False
        except KeyError:
            in_bitmask_dict[num] = False
    return in_bitmask_dict


def pos(expr: int) -> int:
    """
    Simple utility function that returns 0 for all input values below 0, or the input value otherwise.

    :param expr:
    :return:
    """
    if expr < 0:
        return 0
    return expr


def neg(expr: int) -> int:
    """
    Simple utility function that returns 0 for all input values above 0, or the input value otherwise.

    :param expr:
    :return:
    """
    if expr > 0:
        return 0
    return expr


def print_grid(input_grid: Graph):
    """
    Prints the current field grid. Empty nodes are represented by spaces, nodes containing players
    by O's, and nodes containing enemies by X's.

    :param input_grid:
    :return:
    """
    x, y = input_grid.get_grid_width_height()

    for iy in reversed(range(0, y)):
        row = []
        for ix in range(0, x):
            held = input_grid.nodes[iy * x + ix].holds
            if held is None:
                row.append("- ")
            elif held.__class__ == Enemy:
                row.append("X ")
            elif held.__class__ == Player:
                row.append("O ")
        print(" ".join(row))


def find_inconsistencies():
    """
    Function intended to search character data files for skills in incorrect categories.

    :return:
    """

    for index in [9, 10, 11, 12, 13]:
        skill_list = []
        cat = None
        all_skills = {}
        temp_set = set()
        for key, value in players_data[1].items():
            for rarity in range(5):
                iskill = value["skills"][rarity][index]

                if iskill is not None:
                    all_skills[iskill] = (skills_data[1][iskill], key)
                    skill_list.append(skills_data[1][iskill]["category"])
                    cat = skill_list[0]

        if len(set(skill_list)) in [1, 0]:
            print("Category is", cat, "for index", index)
        else:
            print("Index", index, "is an aberrant")
            print("Counts:", ["Cat " + str(i) + ": " + str(skill_list.count(i)) for i in set(skill_list)])
            temp_set = set(skill_list)
            temp_dict = {k: v for k, v in zip([skill_list.count(i) for i in temp_set], [i for i in temp_set])}
            wrong_cat = temp_dict[min(temp_dict.keys())]
            print("Wrong cat:", wrong_cat)
            for iskill, tup in all_skills.items():
                value = tup[0]
                key = tup[1]
                if value["category"] == wrong_cat:
                    print("On hero:", key, "(" + str(players_data[1][key]["roman"]) + ")\n\t", value["id_tag"], ",",
                          translate_jp_to_en_dict(value, english_data, is_skill=True))

        print("Index", index, "has", temp_set)
        print("")


# I mean, I suppose the below would work with floats, but floating-point arithmetic can lead to rounding
# issues and stuff that I don't feel like dealing with
def ones(x: int) -> int:
    """
    Simple utility function to return the one's place digit of a number.

    :param x:
    :return:
    """
    return x % 10


def tens(x: int) -> int:
    """
    Simple utility function to return the ten's place digit of a number.

    :param x:
    :return:
    """
    return floor(x / 10) % 10


def hundreds(x: int) -> int:
    """
    Simple utility function to return the hundreds' place digit of a number.

    :param x:
    :return:
    """
    return floor(x / 100) % 10


def tens_ones(x: int) -> int:
    """
    Simple utility function to return a number composed of the one's and ten's place digits
    of the input number.

    :param x:
    :return:
    """
    return x % 100


# could work with floats, but that's not what it's used for here
def in_range(away: Point, origin: Point, distance: int):
    """
    Returns boolean denoting whether `away` coordinate is within `distance` spaces of `origin`
    coordinates or not.

    :param away:
    :param origin:
    :param distance:
    :return:
    """
    if get_distance_from_tuples(away, origin) > distance:
        return False
    return True


condition_dict = {
    "within_range": "in_range(node.data, origin, distance)",
    "within_columns": "in_range((node.data[0], 0), (origin[0], 0), distance)",
    "within_rows": "in_range((0, node.data[1]), (0, origin[1]), distance)",
    "in_cardinals": "node.data[0] == origin[0] or node.data[1] == origin[1]",
    "within_area": "in_range((node.data[0], 0), (origin[0], 0), ones(distance)) and "
                   "in_range((0, node.data[1]), (0, origin[1]), tens(distance))"
}


def within_range_abstracted(unit: Character, skill: Optional[Skill], condition: str = "within_range",
                            grid: Graph = GRID, distance_override=0) -> List[Character]:
    """
    Returns a list of Character instances whose position is within :attr:`Skill.skill_range`
    spaces of unit

    .. note::
       **Excludes 'unit'**

    """

    within_range_list = list()

    origin = unit.pos
    # CHECK: Does this always work or should I just use an if statement?
    distance = distance_override or skill.skill_range

    for node in grid.nodes:
        # CHECK: Should this exclude unit?
        if node.holds and node.holds != unit and eval(condition_dict[condition]):
            within_range_list.append(node.holds)

    return within_range_list


WITHIN_RANGE_EX_dict = {0: "within_range",  # within range distance of unit
                        1: "within_range",  # same as 0; used by duo skills
                        2: "within_area",  # within ONES(distance) rows and TENS(distance) columns of unit
                        3: "in_cardinals",  # in cardinal directions of unit
                        4: "within_columns",  # within distance columns of unit
                        5: "within_rows",  # within distance rows of unit
                        }


# returns list of characters within range of unit where range is determined by range_shape
# FIXME: separate range_shape variable not needed? Just use skill.range_shape?
# Fuck it, I'll remove it
# Okay now I'm doing it again but for a different reason
def within_range_ex_abstract(unit: Character, skill: Optional[Skill], grid: Graph = GRID,
                             range_shape_override: str = ""):
    range_shape = range_shape_override or WITHIN_RANGE_EX_dict[skill.range_shape]
    return within_range_abstracted(unit, skill, range_shape, grid)


def foes(items: Iterable, unit: Character) -> list:
    """
    Takes a list of Character objects, 'items', and returns a filtered list containing only characters not
    on the same team as 'unit' (teams are based on the class of 'unit', e.g if 'unit' is of class Player, list
    will be comprised of all non-Player characters in 'items').

    :param items:
    :param unit:
    :return:
    """
    # ensures unit is a subclass of Character
    # issubclass(unit.__class__, Character)
    if isinstance(unit, Character) and unit.__class__ != Character:
        return [i for i in items if i.__class__ != unit.__class__]
    else:
        raise ValueError("Unit does not belong to a team")


def allies(items: Iterable, unit: Character) -> list:
    """
        Takes a list of Character objects, 'items', and returns a filtered list containing only characters
        on the same team as 'unit' (teams are based on the class of 'unit', e.g if 'unit' is of class Player,
        list will be comprised of all Player characters in 'items'). Note: the result is inclusive of 'unit'
        in order to keep consistent with the output of the foes() function.

        :param items:
        :param unit:
        :return:
        """
    # ensures unit is a subclass of Character
    # issubclass(unit.__class__, Character)

    if isinstance(unit, Character) and unit.__class__ != Character:
        return [i for i in items if i.__class__ == unit.__class__]
    else:
        raise ValueError("Unit does not belong to a team")


def get_players() -> List[Character]:
    """
    Returns a list of all Player instances in char_list

    :return:
    """
    return [i for i in char_list if i.__class__ == Player]


def get_enemies() -> List[Character]:
    """
    Returns a list of all Enemy instances in char_list

    :return:
    """
    return [i for i in char_list if i.__class__ == Enemy]


def hp_between(min_hp_percent: int, max_hp_percent: int, unit: Character):
    # TODO: Add current_stats (hp affected by damage, others by chills and visible debuffs)
    # TODO: Add combat_stats (not full stats, but stat buffs/debuff that should be added to current_stats)

    if min_hp_percent / 100 <= unit.hp / unit.stats["hp"] <= max_hp_percent / 100:
        return 1
    return 0
    pass


def counter(unit: 'Character'):
    """
    Unit can counterattack regardless of opponent’s range

    :param unit:
    :return:
    """
    unit.counter = True


def no_counter(unit: 'Character'):
    """
    Unit cannot counterattack

    :param unit:
    :return:
    """
    unit.no_counter = True


def follow_up(follow_up_value: int, unit: 'Character'):
    """
    If `follow_up_value` is 1, unit makes a guaranteed follow-up attack, if `follow_up_value` is
    -1 unit cannot make a follow-up attack.

    :param follow_up_value: 1 or -1
    :param unit:
    :return:
    """
    unit.follow_up += follow_up_value
    # FIXME? I think this wrong but idk
    unit.follow_up_value = 1 if follow_up_value > 1 else -1 if follow_up_value < -1 else follow_up_value


# FIXME: This code looks like it can be improved
def null_follow_up(neut_guarantee_foe: bool, neut_prevent_unit: bool, unit: 'Character', enemy: 'Character'):
    if neut_guarantee_foe:
        follow_up(-1, enemy)

    if neut_prevent_unit:
        follow_up(1, unit)


def vantage(unit: 'Character'):
    """
    Unit can counterattack before opponent’s first attack

    :param unit:
    :return:
    """
    unit.vantage = True


def desperation(unit: 'Character'):
    """
    Unit can make a follow-up attack before opponent can counterattack

    :param unit:
    :return:
    """
    unit.desperation = True


def brave(unit: 'Character'):
    """
    Unit attacks twice

    :param unit:
    :return:
    """
    unit.brave = True


def raven(unit: 'Character'):
    """
    Grants weapon-triangle advantage to unit against colorless opponents,
    and inflicts weapon-triangle disadvantage on colorless opponents during combat.

    :param unit:
    :return:
    """
    unit.raven = True


def adaptive(unit: 'Character'):
    """
    Calculates unit’s damage during combat using the lower of opponent’s Def or Res

    :param unit:
    :return:
    """
    unit.adaptive = True


def adaptive_aoe(unit: 'Character'):
    """
    Calculates damage from unit’s area-of-effect Specials using the lower of opponent’s Def or Res

    :param unit:
    :return:
    """
    unit.adaptive_aoe = True


def wrathful_staff(unit: 'Character'):
    """
    Calculates damage from unit’s staff like other weapons

    :param unit:
    :return:
    """
    unit.wrathful_staff = True


# TODO: Add functionality
def charge(mode: int, charge_num: int, unit: 'Character'):
    if mode == 0:
        # grants/inflicts Special cooldown charge +x to/on u per attack during combat

        pass
    elif mode == 1:
        # grants/inflicts Special cooldown charge +x to/on u per u’s attack during combat

        pass
    elif mode == 2:
        # grants/inflicts Special cooldown charge +x to/on u per opponent of u’s attack during combat

        pass
    pass


# aether/sol/noontime and the like
def combat_add_hp(hp_change: int, unit: 'Character'):
    unit.hp += hp_change
    unit.hp = min(unit.hp, unit.stats["hp"])


# savage blow and stuff
def map_add_hp(hp_change: int, unit: 'Character'):
    unit.hp += hp_change
    if unit.hp > 0:
        unit.hp = min(unit.hp, unit.stats["hp"])
    else:
        # units cannot be killed by out-of-combat damage
        unit.hp = 1

    pass


# Had to use FunctionType because for some reason 'function' didn't work? Gave me an unresolved reference
# Screw it, I don't like FunctionType
# Actually, Callable is a function, not a type
# Hmmmmmmmmmmmmmmmmmmm
def count_around(unit: Character, unit_type: 'Callable', context: Union['Slid', 'Skill']) -> int:
    # FIXME: Improve docstring
    """
    If context is:
        SkillLimit (Slid instance):
            returns the number of 'unit_type' within param1 spaces of 'unit' (excluding 'unit')
        SkillAbility (Skill instance):
            returns the number of 'unit_type' within skill_range spaces of 'unit' (excluding 'unit')

    :param unit: Unit to use as origin
    :param unit_type: Condition to evaluate
    :param context: Context function is being used in
    :return:
    """

    # FIXME: Improve context variable, it's terrible right now and the error string is just plain confusing

    if isinstance(context, Slid):
        range = context.param1
    elif isinstance(context, Skill):
        range = context.skill_range
    else:
        raise ValueError("Context can be either 'limit' (Slid instance) or 'ability' (Skill instance), "
                         "{0} was supplied".format(context))

    # FIXME: Combine the below lines after testing
    # within_range doesn't return unit so that means count_around doesn't either
    char_around = within_range_abstracted(unit, None, "within_range", distance_override=range)

    # filters nearby characters by 'unit_type' condition
    cond_char = unit_type(char_around, unit)

    # returns number of nearby characters that satisfy condition
    return len(cond_char)


# could implement using within_range, but I think this is better
# CHECK: This thing is confusing
def unit_near(self, other_unit: 'Character', skill: Skill):
    """
    If unit is :func:`within_range` of unit

    :param self:
    :param other_unit:
    :param skill:
    :return:
    """
    return in_range(self.pos, other_unit.pos, skill.skill_range)


def neighborhood(unit: Character, skill: Skill) -> List[Character]:
    """
    Unit and units on unit’s team :func:`within_range` of unit

    :param unit:
    :param skill:
    :return:
    """
    nearby = within_range_abstracted(unit, skill, "within_range")

    # second part is not needed because allies() is inclusive
    return allies(nearby, unit)  # + [unit]


def neighborhood_ex(unit: Character, skill: Optional[Skill], range_shape_override: str = "") -> List[Character]:
    nearby = within_range_ex_abstract(unit, skill, range_shape_override=range_shape_override)

    # second part is not needed because allies() is inclusive
    return allies(nearby, unit)  # + [unit]


def cooldown(cooldown: int, unit: Character):
    unit.special_cd += cooldown

    # if special_cd is below 0, set to 0
    unit.special_cd = max(0, unit.special_cd)
    # if special_cd is above max, set to max
    unit.special_cd = min(unit.special_cd, unit.max_special_cd)


def buff(skill: Skill, unit: Union[Character, Iterable[Character]]):
    # TODO: Make compatible with buffs and debuffs, add checks to only increase if greater than current buff
    # TODO: Buffs last for 1 turn, debuffs last through next action
    for key in skill.skill_params.keys():
        unit.buffs[key] = skill.skill_params[key]


def buff2(skill: Skill, unit: Union[Character, Iterable[Character]]):
    for key in skill.skill_params2.keys():
        unit.buffs[key] = skill.skill_params2[key]


status_dict = {0: "Gravity", 1: "Panic", 2: "No counterattacks", 3: "March", 4: "Triangle Adept", 5: "Guard",
               6: "Air Orders", 7: "Isolation", 8: "Effective against dragons", 9: "Bonus doubler",
               10: "Dragon shield", 11: "Svalinn shield", 12: "Dominance", 13: "Resonance: Blades", 14: "Desperation"}


def status(status_id: int) -> str:
    """
    Converts status id to status name

    :param status_id:
    :return:
    """
    return status_dict[status_id]


def add_status(status_effect: str, unit: Character):
    """
    Grants/inflicts status to/on unit

    :param status_effect:
    :param unit:
    :return:
    """
    unit.status_effects[status_effect] = True


def special_damage(damage):
    pass


def luna(reduction_percent):
    pass


# TODO: Write the logic for these
def bonus_broad(unit: Character):
    # do calculations here

    return 0


def bonus_narrow(unit: Character):
    if buff_total(unit) > 0:
        return 1
    return 0


def penalty_broad(unit: Character):
    # same as above, but reversed

    return 0


def penalty_narrow(unit: Character):
    return 0


def dragon(items: Iterable[Character]) -> List[Character]:
    return [i for i in items if 16 <= i.weapon_type < 20]


def beast(items: Iterable[Character]) -> List[Character]:
    return [i for i in items if 20 <= i.weapon_type < 24]


def not_dragon(items: Iterable[Character]) -> List[Character]:
    return [i for i in items if not 16 <= i.weapon_type < 20]


def not_beast(items: Iterable[Character]) -> List[Character]:
    return [i for i in items if not 20 <= i.weapon_type < 24]


def combine_buffs_debuffs(unit: Character):
    # Could also do this, more human, {stat: unit.buffs[stat] + unit.debuffs[stat] for stat in unit.stats}
    return {stat: buff + unit.debuffs[stat] for stat, buff in unit.buffs}


def buff_total(unit: Character) -> int:
    return sum(unit.buffs.values())


def debuff_total(unit: Character) -> int:
    return abs(sum(unit.debuffs.values()))


def get_direction(unit: Union[Character, Tuple], target: Union[Character, Tuple]) -> Tuple:
    if isinstance(unit, Character):
        first = unit.pos
    elif isinstance(unit, tuple):
        first = unit
    else:
        raise TypeError

    if isinstance(target, Character):
        second = target.pos
        pass
    elif isinstance(target, tuple):
        second = target
    else:
        raise TypeError

    if get_distance_from_tuples(first, second) > 1:
        raise ValueError("Positions are not adjacent, thus direction is not cardinal")
    elif get_distance_from_tuples(first, second) == 0:
        raise ValueError("First and second positions must be different")

    if first[0] != second[0]:
        return (first[0] - second[0], 0)
    return (0, first[1] - second[1])


def give_action(unit: Character):
    pass


# CHECK: is this how it should be done? Should I keep debuff values for future reference?
def convert_penalties_to_bonuses(unit: Character):
    for key in unit.stats.keys():
        unit.buffs[key] = unit.debuffs[key]
        unit.debuffs[key] = 0


# CHECK: is this how it should be done? Should I keep buff values for future reference?
def convert_bonuses_to_penalties(unit: Character):
    for key in unit.stats.keys():
        unit.debuffs[key] = unit.buffs[key]
        unit.buffs[key] = 0


def neutralize_penalties(unit: Character):
    # TODO: Neutralize penalties on unit
    pass


def spectrum_buff(units: Union[Character, Iterable[Character]], buff: int):
    if issubclass(type(units), Iterable):
        pass
    elif isinstance(units, Character):
        units = [units]
    else:
        raise TypeError("Input must be a Character type or an Iterable containing Character types")

    for unit in units:
        for key in ["atk", "spd", "def", "res"]:
            unit.buffs[key] = max(unit.buffs[key], buff)


def spectrum_debuff(units: Union[Character, Iterable[Character]], debuff: int):
    if issubclass(type(units), Iterable):
        pass
    elif isinstance(units, Character):
        units = [units]
    else:
        raise TypeError("Input must be a Character type or an Iterable containing Character types")

    for unit in units:
        for key in ["atk", "spd", "def", "res"]:
            unit.debuffs[key] = min(unit.debuffs[key], debuff)


# ==============

class Slid:
    """Creates self.param1 and self.param2"""

    def __init__(self, skill, id):
        self.skill = skill
        if id == 1:
            self.param1 = skill.limit1_params[0]
            self.param2 = skill.limit1_params[1]
        elif id == 2:
            self.param1 = skill.limit2_params[0]
            self.param2 = skill.limit2_params[1]


def find(skill, slid_value):
    # finds id with matching value and returns Slid object
    for id, id_value in enumerate([skill.limit1_id, skill.limit2_id]):
        if id_value == slid_value:
            return Slid(skill, id + 1)
    raise LimitIdNotFound("Search for slid{0} did not yield any results".format(slid_value))
    # return -1


# GENERAL DEFINITIONS END
# ============================================================================================================


class GameLoop:
    def __init__(self):
        self.turn = 0  # 1?
        self.phase = "player"
        self.running = True

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, value):
        self.turn += 1
        self._phase = value

    def main(self, autobattle=False):

        # self.swap_phase()

        while self.running:
            # self.player_phase()
            # self.enemy_phase()
            #
            # instruction = input()
            # self.process_instruction(instruction)

            self.battle_phase()

    def process_instruction(self, instruction: str):
        tokens: List[str] = instruction.split(" ")
        command = tokens[0]
        if len(tokens) > 1:
            args = tokens[1:]
        else:
            args = []

        if command == "chars":
            print("Player characters:")
            players = [i for i in char_list if i.__class__ == Player]
            if len(players) != 0:
                for i in players:
                    print("\t" + str(i))
            else:
                print("None")
            print("Enemy characters:")
            enemies = [i for i in char_list if i.__class__ == Enemy]
            if len(enemies) != 0:
                for i in enemies:
                    print("\t" + str(i))
            else:
                print("None")

        elif command == "create":
            char_type = args[0].lower()


        elif command == "exit":
            self.running = False
        else:
            print("No such command, attempting exec")
            try:
                exec(instruction)
            except Exception as e:
                print("Failed exec: ", e)

        pass

    def swap_phase(self):
        print("Starting swap phase")

        # do something

        self.battle_phase()
        pass

    def player_phase(self):
        print("Starting player phase")
        self.phase = "player"
        players = get_players()
        self.start_of_turn(players)

        print_grid(GRID)

        print(*[f"{i}: {player.name} {player.pos};" for i, player in enumerate(players)])
        # print(*[f"{enemy.name} {enemy.pos};" for enemy in get_enemies()])

        index = int(input("Select unit: ").strip())
        action = input("Select action move (m) or attack (a): ").strip()

        if action == "a":
            pos = input("Give enemy position: ").strip()
            x, y = pos.split(",")[0], pos.split(",")[1]
            x = int(x.strip())
            y = int(y.strip())
            players[index].attack_node((x, y))

        if action == "m":
            pos = input("Give position to move to: ").strip()
            x, y = pos.split(",")[0], pos.split(",")[1]
            x = int(x.strip())
            y = int(y.strip())
            players[index].move((x, y))

    def enemy_phase(self):
        print("Starting enemy phase")
        self.phase = "enemy"
        enemies = get_enemies()
        self.start_of_turn(enemies)

    @staticmethod
    def get_phase(self):
        while True:
            for ph in [self.player_phase, self.enemy_phase]:
                yield ph

    def battle_phase(self):
        print("Starting battle phase")

        while not (get_players() == [] or get_enemies() == []):
            next(self.get_phase(self))()

        if self.phase == "player":
            print("Victory")
        elif self.phase == "enemy":
            print("Defeat")

        self.running = False

    def evaluate_skills(self, characters: Union[Character, Iterable[Character]],
                        timing_contexts: Iterable[int]):
        if not isinstance(characters, Iterable):
            characters = [characters]

        for character in characters:
            assert isinstance(character, Character)

            # TODO: Determine SAID order
            for category, skill in dict(character.equipped_skills, weapon=character.weapon).items():
                if not skill is None:
                    assert isinstance(skill, Skill)
                    if skill.timing_id in timing_contexts:
                        # do skill stuff here; skill.activate() or whatever
                        # I have indeed made it be "skill.activate() or whatever"
                        print(f"Activating {skill}")
                        skill.activate(skill=skill, unit=character)

                        # CHECK: Change to evaluate for each SAID rather than each character here?

                        pass

    # CHECK: All of the below

    def start_of_turn(self, characters):
        print("Starting turn")

        self.evaluate_skills(characters, [8, 12, 13, 22, 25, 27])

    def upon_movement(self, unit: Character):

        self.evaluate_skills(unit, [9, 24, 26])

        pass

    def after_movement(self, unit: Character):

        self.evaluate_skills(unit, [19])
        pass

    def before_combat(self, unit: Character, foe: Character):

        self.evaluate_skills([unit, foe], [1, 5, 12, 15, 21, 23, 28])
        pass

    def during_combat(self, unit: Character, foe: Character):

        self.evaluate_skills([unit, foe], [1, 2, 12, 15, 20, 21, 23, 24, 28])
        pass

    def after_combat(self, unit: Character, foe: Character):

        self.evaluate_skills([unit, foe], [1, 3, 6, 15, 21, 26, 27])
        pass

    def attack(self, unit: Character, foe: Character):

        self.evaluate_skills([unit, foe], [3, 4, 10, 11, 12, 13, 21, 28])
        pass

    def use_assist(self, unit: Character, target: Character):

        self.evaluate_skills([unit, target], [0, 7, 14, 16, 17, 22, 23])
        pass

    def use_duo_skill(self, unit: Character):

        self.evaluate_skills([unit], [0])
        pass

    def calc_arena_score(self, characters):

        self.evaluate_skills(characters, [18])
        pass


def program_instructions():
    # testchar = Character.from_dict(players_data[0]["PID_Clarisse"], weapon="SID_鉄の弓", pos=(1, 1))
    # print(testchar.stats)
    # testchar.unequip_weapon()
    # print(testchar.stats)
    # testchar.equip_weapon("SID_狙撃手の弓")
    # print(testchar.stats)
    #
    # gl = GameLoop()
    # gl.main()
    from Code.FEH_character_search import get_character

    testchar = Enemy.from_dict(players_data[0][get_character("Aversa", players_data)], pos=(1, 1),
                               rarity=5, level=40, weapon="SID_ノスフェラート")

    testchar2 = Player.from_dict(players_data[0][get_character("Alphonse", players_data)], pos=(2, 1), rarity=5,
                                 level=40,
                                 weapon="SID_銀の剣")

    testchar3 = Player.from_dict(players_data[0][get_character("Alphonse", players_data)], pos=(3, 1), rarity=5,
                                 level=40,
                                 weapon="SID_銀の剣")

    # print("STATS:", players_data[0]["PID_Ophelia"]["base_stats"])
    # print()
    # testchar2 = Player.from_dict(players_data[0]["PID_Ophelia"], pos=(2, 1), rarity=5, level=40,
    #                              weapon="SID_魔書ミステルトィン", special_cd=4, max_special_cd=4)
    # print()
    # testchar3 = Player.from_dict(players_data[0]["PID_Ophelia"], pos=(3, 1), rarity=5, level=40,
    #                              weapon="SID_魔書ミステルトィン", special_cd=4, max_special_cd=4)
    # print()
    # print("STATS", players_data[0]["PID_Ophelia"]["base_stats"])

    loop = GameLoop()
    loop.main()

    # for skill in skills_data[1].values():
    #     if skill["timing_id"] == 8 and (skill["limit1_id"] == 9 or skill["limit2_id"] == 9):
    #         print(skill)

    # for skill in skills_data[1].values():
    #     # slid0 means the skill does not have an activation condition
    #     if (skill["limit1_id"] == skill["limit2_id"]) and (skill["limit1_id"] != 0 and skill["limit2_id"] != 0):
    #         print(skill)

    # x = Skill.from_dict(skills_data[0]["Desperation 3"])
    # with stid1.SLID(x, testchar) as sl:
    #     print(sl.__dict__)

    # print(len(players_data[0]))
    # data0 = {v["id_num"] for k, v in players_data[0].items()}
    # print(len(players_data[1]))
    # data1 = {v["id_num"] for k, v in players_data[1].items()}
    # print(data1.symmetric_difference(data0))
    # print(len(players_data[2]))

    pass


if __name__ == "__main__":
    # load all necessary data
    skills_data, players_data, enemies_data, weapons_data, english_data, growth_data, move_data, \
    stage_encount_data, terrain_data = load_files(get_simple_names=True)

    weapon_data_by_index = {v["index"]: v for v in weapons_data[1].values()}

    colors_by_weapon_index = [1, 2, 3, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 0, 1, 2, 3, 0, 1, 2, 3, 0]
    weapon_index_to_color_dict = {k: v for k, v in zip([i for i in range(24)], colors_by_weapon_index)}

    # from Code.SkillTimingContexts import (
    #     stid0, stid1, stid2, stid3, stid4, stid5, stid6, stid7, stid8, stid9, stid10,
    #     stid11, stid12, stid13, stid14, stid15, stid16, stid17, stid18, stid19, stid20,
    #     stid21, stid22, stid23, stid24, stid25, stid26, stid27, stid28
    # )

    from Code.SkillTimingContexts import *

    # ========================================================================================================

    prog_start = time()
    program_instructions()
    prog_stop = time()
    print("\nTime elapsed:", prog_stop - prog_start)
    print("Program execution complete; terminating process")

# TODO: Add getter/setter properties for unit attributes like hp that trigger on_damage(), check_is_dead(), etc

# TODO: Add __slots__ that is initialized at runtime to the values retrieved from the json files + predefined

# TODO Final Boss: Finish this
