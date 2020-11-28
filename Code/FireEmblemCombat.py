from DijkstraAlgorithm_Speedy_Custom import *
from math import trunc, floor  # ceil
from Code.FireEmblemLoadJsonDataFiles import load_files_kag_calc_ver

# FIXME: change casings
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
    "continous auto": "on",
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

data_assists, data_driveskills, data_heroes, data_passives, data_specials, data_weapons, data_blessings, \
data_refinements, data_support_bonus = load_files_kag_calc_ver(get_assists=False, get_driveskills=False,
                                                               get_passives=False,
                                                               get_specials=False, get_blessings=False,
                                                               get_support_bonus=False)

grid = Graph.init_as_grid(6, 8)


# print(grid.nodes)

def get_distance_from_tuples(self, enemy):
    return abs(enemy[0] - self[0]) + abs(enemy[1] - self[1])


move_type_to_move_range = {"Armored": 1,
                           "Infantry": 2,
                           "Flier": 2,
                           "Cavalry": 3}

weapon_to_attack_range = {"Sword": 1,
                          "Lance": 1,
                          "Axe": 1,
                          "Breath": 1,
                          "Beast": 1,
                          "Bow": 2,
                          "Red Tome": 2,
                          "Blue Tome": 2,
                          "Green Tome": 2,
                          "Dagger": 2,
                          "Staff": 2}


def pos(expr):
    if expr < 0:
        return 0
    return expr


def neg(expr):
    if expr > 0:
        return 0
    return expr


weapon_advantage = {
    "Red": "Green",
    "Blue": "Red",
    "Green": "Blue"
}


#
# class Weapon:
#     def __init__(self, name="None", color=None, weapon_type=None, might=0, damage_type=None, sp=0, exclusive=False,
#                  desc=""):
#         for k, v in [_ for _ in locals().items()][::-1]:
#             setattr(self, k, v)
#         self.range = weapon_to_attack_range[weapon_type]


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


#
# weapons = {
#     "Iron Sword": Weapon("Iron Sword", "red", "Sword", 6, "physical", 50, False),
#     "Iron Lance": Weapon("Iron Lance", "blue", "Lance", 6, "physical", 50, False),
#     "Iron Axe": Weapon("Iron Axe", "green", "Axe", 6, "physical", 50, False),
#     "Fire": Weapon("Fire", "red", "Tome", 4, "magical", 50, False),
#     "Light": Weapon("Light", "blue", "Tome", 4, "magical", 50, False),
#     "Wind": Weapon("Wind", "green", "Tome", 4, "magical", 50, False),
# }

weapons = {}

for weapon in data_weapons:
    # print(data_weapons[weapon])
    # print(len(data_weapons[weapon]))
    weapons[weapon] = Weapon.from_dict(data_weapons[weapon])

    # print(classWeapon)
    # print(classWeapon.name)


# classWeapon = Weapon(name = "My name")
# print(classWeapon)
# print(classWeapon.name)


# TODO: Overhaul for compatibility with data from FireEmblemLoadJsonDataFiles.load_files()
class Character(object):
    def __init__(self, name, HP, ATK, SPD, DEF, RES, weapon_type="Sword", color="Red", pos=None, move_type="Infantry",
                 move_range=None, weapon=None, affinity=0):

        # print([k for k in locals().items()][::-1])
        for k, v in [_ for _ in locals().items()][::-1]:
            setattr(self, k, v)
        if pos is not None:
            self.node = grid.nodes[grid.get_index_from_xy(pos)]
            self.node.holds = self
        if move_range is None:
            self.move_range = move_type_to_move_range[self.move_type]
        self.range = weapon_to_attack_range[self.weapon_type]
        if weapon is not None:
            self.equip_weapon(weapon)

    @classmethod
    def create_from_json(cls, hero_name):
        hero = data_heroes[hero_name]
        hero_stats = hero["base_stat"]["star_5"]
        return cls(name=hero["name"], HP=hero_stats["hp"], ATK=hero_stats["atk"], SPD=hero_stats["spd"],
                   DEF=hero_stats["def"],
                   RES=hero_stats["res"], weapon_type=hero["weapon_type"], color=hero["color"],
                   move_type=hero["move_type"], weapon=weapons[hero["weapon"][-1]])

    def equip_weapon(self, weapon):
        try:
            if weapon.type == self.weapon_type and weapon.color == self.color:
                self.weapon = weapon
                self.ATK = self.ATK + weapon.might
            else:
                print("Incompatible weapon")
        except AttributeError as e:
            print("Oh boy an error!", e)

    def unequip_weapon(self):
        if self.weapon != None:
            self.ATK = self.ATK - self.weapon.might
            self.weapon = None

    def get_distance(self, enemy):
        return abs(enemy.pos[0] - self.pos[0]) + abs(enemy.pos[1] - self.pos[1])

    def calc_weapon_triangle(self, enemy):
        if enemy.color == weapon_advantage[self.color]:
            return 0.2
        elif self.color == weapon_advantage[enemy.color]:
            return -0.2
        elif self.color == enemy.color or self.color == "gray" or enemy.color == "gray":
            return 0

    def calc_effectiveness(self, enemy):
        if self.weapon.type == "Bow" and enemy.move_type == "Flier":
            return 1.5
        return 1

    def calc_boosted_damage(self, enemy):
        return 0
        # TODO: add functionality

    def attack_enemy(self, enemy):
        if enemy.pos == self.pos:
            print("You can't attack yourself silly")
            return None
        if enemy.HP > 0:
            if self.get_distance(enemy) == self.range:
                print("Enemy in range, commencing attack")
                mitigation = enemy.DEF if self.weapon.magical == "false" else enemy.RES

                damage = pos(floor(self.ATK * self.calc_effectiveness(enemy)) + trunc(
                    floor(self.ATK * self.calc_effectiveness(enemy)) * (self.calc_weapon_triangle(enemy) * (
                            self.affinity + 20) / 20)) + self.calc_boosted_damage(enemy) - mitigation)
                enemy.HP = enemy.HP - damage

                if enemy.HP > 0:
                    print(self.name, "dealt", damage, "damage,", enemy.name, "has", enemy.HP, "HP remaining")
                else:
                    print(self.name, "dealt", damage, "damage,", enemy.name, "has been defeated")
                    grid.nodes[grid.get_index_from_xy(enemy.pos)].holds = None
                return None
            print("Enemy not in range")
        else:
            print("Enemy has already been defeated")

    def attack_node(self, node):
        enemy = grid.nodes[grid.get_index_from_xy(node)].holds
        if enemy is not None:
            self.attack_enemy(enemy)
        else:
            print("There is no enemy at position", node)

    def move(self, new_pos):
        print(self.name, "moved", get_distance_from_tuples(self.pos, new_pos), "spaces from", self.pos, "to", new_pos)
        grid.nodes[grid.get_index_from_xy(self.pos)].holds = None
        self.pos = new_pos
        grid.nodes[grid.get_index_from_xy(new_pos)].holds = self

    def fight(self, enemy):
        self.attack_enemy(enemy)
        if enemy.HP > 0:
            enemy.attack_enemy(self)
            if self.SPD >= enemy.SPD + 5 and self.HP > 0:
                self.attack_enemy(enemy)
            elif enemy.SPD >= self.SPD + 5:
                enemy.attack_enemy(self)

    def move_to_attack(self, enemy):
        endpoints = grid.dijkstra(enemy.pos, eval_to_length=self.range)

        # pprint([(weight, [n.data for n in node]) for (weight, node) in endpoints])

        endpoints = [i for i in
                     [points[-1] if get_distance_from_tuples(enemy.pos, points[-1].data) == self.range else None for
                      (weight, points) in endpoints] if i is not None]

        # pprint([i.data if i is not None else None for i in endpoints])

        endpoints = [endpoint for endpoint in endpoints if
                     get_distance_from_tuples(self.pos, endpoint.data) <= self.move_range]

        # print([endpoint.data for endpoint in endpoints])

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

    def move_towards(self, enemy):
        weight, nodes = grid.dijkstra(self.pos, enemy.pos, only_end=True)[0]

        distance = get_distance_from_tuples(self.pos, enemy.pos)

        if distance == self.range:
            print(self.name, "is already in range and does not move")

        if distance > self.range:
            move_distance = distance - self.range
            if move_distance > self.move_range:
                self.move(nodes[self.move_range].data)
            else:
                self.move(nodes[move_distance].data)
            pass

        if distance < self.range:
            print(self.name, "is too close and moves further away")


# TODO: add proper AI
class Enemy(Character):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    pass


class Player(Character):
    pass


# for i in dir(grid.nodes[0]):
#     print(i, grid.nodes[0].__getattribute__(i))

def print_grid(grid):
    x, y = grid.get_grid_width_height()

    for iy in reversed(range(0, y)):
        row = []
        for ix in range(0, x):
            held = grid.nodes[iy * x + ix].holds
            if held == None:
                row.append("  ")
            elif held.__class__ == Enemy:
                row.append("x ")
            elif held.__class__ == Player:
                row.append("O ")
        print(row)


def enemy_phase(enemies):
    pass


def swap_phase(players):
    pass


def player_phase(players):
    if CONFIG["starting a map"] == "swap spaces":
        swap_phase(players)

    for player in players():
        select_action()


def battle_phase(characters):
    players = set()
    enemies = set()
    for character in characters:
        if isinstance(character, Player):
            players.add(character)
        elif isinstance(character, Enemy):
            enemies.add(character)

    player_phase(players)

    enemy_phase(enemies)

    pass


def select_action():
    # actions: attack / move to attack, heal, stay, rally assist, movement skill
    # select action logic here
    action = "attack"
    if action == "attack":
        opponent = select_enemy()
    pass


def select_enemy():
    pass


def program_instructions():
    Char = Player("Steve", 1, 5, 8, 4, 5, pos=(1, 1), weapon_type="Red Tome", weapon=weapons["fire"])

    Gob = Enemy("Gobby", 5, 4, 3, 2, 1, pos=(6, 3), weapon=weapons["iron-sword"])

    Abel = Character.create_from_json("abel-the-panther")

    Char.move_to_attack(Gob)

    Char.move_towards(Gob)
    Char.move_towards(Gob)
    Char.move_towards(Gob)
    Char.move_towards(Gob)
    Gob.move_towards(Char)

    Char.move_to_attack(Gob)

    pass


if __name__ == "__main__":
    program_instructions()
    print("Program execution complete; terminating process")
