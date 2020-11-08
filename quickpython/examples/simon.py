"""
/games/simon.py

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

__version_info__ = (1, 0, 0, "final", 0)
__version__ = "{0}.{1}.{2}{3}{4}".format(
    *[str(n)[0] if (i == 3) else str(n) for (i, n) in enumerate(__version_info__)]
)


import os
import random
import time

import colorama
import pyfiglet

COLORS = {
    "easy": [
        (colorama.Back.RED, "red"),
        (colorama.Back.GREEN, "green"),
        (colorama.Back.BLUE, "blue"),
        (colorama.Back.YELLOW, "yellow"),
    ],
    "intermediate": [
        (colorama.Back.RED, "red"),
        (colorama.Back.GREEN, "green"),
        (colorama.Back.BLUE, "blue"),
        (colorama.Back.YELLOW, "yellow"),
        (colorama.Back.CYAN, "cyan"),
    ],
    "hard": [
        (colorama.Back.GREEN, "green"),
        (colorama.Back.BLUE, "blue"),
        (colorama.Back.YELLOW, "yellow"),
        (colorama.Back.CYAN, "cyan"),
        (colorama.Back.MAGENTA, "magenta"),
    ],
}

TIMES = {"easy": 0.5, "intermediate": 0.4, "hard": 0.3}


class Simon:
    def __init__(self, difficulty: str):
        """
        initializes a `Simon` object
        """

        self.colors = COLORS[difficulty]
        self.time = TIMES[difficulty]

    def game(self):
        """
        starts the game
        """

        colors = list()

        while True:
            colors.append(random.choice(self.colors))

            for (color, color_name) in colors:
                cls()
                print(
                    """
                ------------------
                |{0}                {1}|
                |{0}                {1}|
                |{0}                {1}|
                |{0}                {1}|
                |{0}                {1}|
                |{0}                {1}|
                |{0}                {1}|
                ------------------
                """.format(
                        color, colorama.Back.RESET
                    )
                )

                time.sleep(self.time)

                cls()
                print(
                    """
                ------------------
                |                |
                |                |
                |                |
                |                |
                |                |
                |                |
                |                |
                ------------------
                """
                )

                time.sleep(self.time)

            print()

            answer = input("> ").replace(" ", "")
            correct = "".join([color_name[0] for (color, color_name) in colors])

            if answer != correct:
                break

        print()
        print("you got {0} correct combinations".format(len(colors) - 1))

    def start(self):
        """
        calls `self.game` in a 'would you like to play again?' loop
        """

        choice = "y"
        while choice.startswith("y"):
            cls()
            print(pyfiglet.figlet_format("Simon Says"))
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

    game = Simon(difficulty)
    game.start()
