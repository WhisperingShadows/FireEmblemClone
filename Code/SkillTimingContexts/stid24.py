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


def slid17(self):
    pass


def slid53(self):
    pass
