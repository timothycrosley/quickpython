"""
/games/memory.py

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
import re
import string
import time

import pyfiglet

GRID_SIZES = {"easy": 6, "intermediate": 10, "hard": 14}

CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"£$%^&*()-_=+[{]};:'@#~,<.>/?\\|`¬áé"


class Memory:
    def __init__(self, difficulty: str):
        """
        initializes a `Memory` object
        """

        self.grid_size = GRID_SIZES[difficulty]
        self.characters = CHARACTERS[: (((self.grid_size // 2) ** 2) * 2)]

        self.message = ""

    def game(self):
        """
        starts the game
        """

        self.known = [" "] * len(self.characters * 2)
        characters = [character for character in self.characters * 2]

        random.shuffle(characters)

        while " " in self.known:
            cls()
            print()

            self.show_grid()

            print()

            if self.message:
                print(self.message)
                print()

                self.message = ""

            coordinates = input("coordinates;\n> ").strip().upper()
            if not self.valid_coordinates(coordinates):
                self.message = "invalid coordinates"
                continue

            first_row, first_column = self.parse_coordinates(coordinates)

            if self.known[(first_row * self.grid_size) + first_column] != " ":
                self.message = "invalid coordinates"
                continue

            self.known[(first_row * self.grid_size) + first_column] = characters[
                (first_row * self.grid_size) + first_column
            ]

            while True:
                cls()
                print()

                self.show_grid()

                print()

                if self.message:
                    print(self.message)
                    print()

                    self.message = ""

                coordinates = input("> ").strip().upper()
                if self.valid_coordinates(coordinates):
                    second_row, second_column = self.parse_coordinates(coordinates)

                    if self.known[(second_row * self.grid_size) + second_column] != " ":
                        self.message = "invalid coordinates"
                        continue

                    self.known[(second_row * self.grid_size) + second_column] = characters[
                        (second_row * self.grid_size) + second_column
                    ]
                    break

                self.message = "invalid coordinates"

            cls()
            print()

            self.show_grid()

            time.sleep(1)

            if (
                not self.known[(first_row * self.grid_size) + first_column]
                == self.known[(second_row * self.grid_size) + second_column]
            ):
                self.known[(first_row * self.grid_size) + first_column] = " "
                self.known[(second_row * self.grid_size) + second_column] = " "

        cls()
        print()

        self.show_grid()

        print()
        print("congrats")

    def parse_coordinates(self, coordinates: str):
        """
        generates a (row : int, column : int) tuple from coordinates

        arguments:
            coordinates :: str   :: the coordinates convert

        returns:
                        :: tuple :: a (row : int, column : int) tuple
        """

        pattern = re.compile(
            r"(?P<column>[A-{0}])(?P<row>{1})".format(
                string.ascii_uppercase[self.grid_size - 1],
                "|".join([str(i) for i in range(1, self.grid_size + 1)][::-1]),
            )
        )
        match = re.match(pattern, coordinates)

        row = int(match.group("row")) - 1
        column = string.ascii_uppercase.index(match.group("column"))

        return (row, column)

    def show_grid(self):
        """"""

        print(
            "       {0}".format(
                "   ".join([character for character in string.ascii_lowercase][: self.grid_size])
            )
        )
        print("     {0}".format("-" * ((self.grid_size * 4) + 1)))

        i = 1
        for (j, k) in enumerate(self.known, 1):
            if j % (self.grid_size) == 0:
                print("| {0} |".format(k))
                print("     {0}".format("-" * ((self.grid_size * 4) + 1)))
            elif j % (self.grid_size) == 1:
                print("  {0:>2} | {1} ".format(i, k), end="")
                i += 1
            else:
                print("| {0} ".format(k), end="")

    def start(self):
        """
        calls `self.game` in a 'would you like to play again?' loop
        """

        choice = "y"
        while choice.startswith("y"):
            cls()
            print(pyfiglet.figlet_format("Memory"))
            print()
            input("enter to play\nctrl + c to quit to main menu\n\n")

            self.game()
            choice = input("\nwould you like to play again?\n> ").strip()

    def valid_coordinates(self, coordinates: str):
        """
        determines whether `coordinates` are valid

        arguments:
            coordinates :: str  :: the coordinates to check

        returns:
                        :: bool :: whether `coordinates` are valid
        """

        pattern = re.compile(
            r"(?P<column>[A-{0}])(?P<row>{1})".format(
                string.ascii_uppercase[self.grid_size - 1],
                "|".join([str(i) for i in range(1, self.grid_size + 1)][::-1]),
            )
        )
        match = re.match(pattern, coordinates)

        if match:
            return True
        return False


if __name__ == "__main__":
    difficulty = None
    while difficulty not in {"easy", "intermediate", "hard"}:
        cls()
        print()
        difficulty = input("difficulty;\n> ").strip()

    game = Memory(difficulty)
    game.start()
