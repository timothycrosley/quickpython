"""
/games/towers.py

    Copyright (c) 2019 ShineyDev
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

__authors__ = [("shineydev", "contact@shiney.dev")]
__maintainers__ = [("shineydev", "contact@shiney.dev")]

__version_info__ = (0, 0, 1, "alpha", 0)
__version__ = "{0}.{1}.{2}{3}{4}".format(
    *[str(n)[0] if (i == 3) else str(n) for (i, n) in enumerate(__version_info__)]
)


import os

import colorama
import pyfiglet

HEIGHTS = {"easy": 3, "intermediate": 4, "hard": 5}


class Towers:
    def __init__(self, difficulty: str):
        """
        initializes a `Towers` object
        """

        self.tower_height = HEIGHTS[difficulty]

    def game(self):
        """
        starts the game
        """

        pass

    def start(self):
        """
        calls `self.game` in a 'would you like to play again?' loop
        """

        choice = "y"
        while choice.startswith("y"):
            cls()
            print(pyfiglet.figlet_format("Towers"))
            print()
            input("enter to play\nctrl + c to quit to main menu\n\n")

            self.game()
            choice = input("\nwould you like to play again?\n> ").strip()


if __name__ == "__main__":
    difficulty = None
    while difficulty not in {"easy", "intermediate", "hard"}:
        cls()
        print()
        difficulty = input("difficulty;\n> ").strip()

    game = Towers(difficulty)
    game.start()
