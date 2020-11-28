from Code import FEH_character_search as char_search


def process_instruction(self, instruction: str):
    tokens: List[str] = instruction.split(" ")
    command = tokens[0]
    args = tokens[1:]

    if command == "chars":
        print("Player characters")
        players = [i for i in char_list if i.__class__ == Player]
        if len(players) != 0:
            for i in players:
                print("\t" + str(i))
        else:
            print("None")
        print("Enemy characters")
        enemies = [i for i in char_list if i.__class__ == Enemy]
        if len(enemies) != 0:
            for i in enemies:
                print("\t" + str(i))
        else:
            print("None")

    elif command == "create":
        char_type = args[0].lower()
        if char_type == "player":
            char_class = Player
            class_data_dict = players_data
        elif char_type == "enemy":
            char_class = Enemy
            class_data_dict = enemies_data
        else:
            raise ValueError("Invalid character type %s" % char_type)

        # TODO: Implement a closest search for dict keys
        char_name = char_search.get_character(' '.join(args[1:]))[0]
        char_class.from_dict(class_data_dict[0][char_name])



    elif command == "exit":
        self.running = False
    else:
        print("No such command")

    pass


if __name__ == '__main__':
    from Code.FireEmblemCombatV2 import *

    while True:
        stdin = input(">>> ")
        process_instruction(None, stdin)
