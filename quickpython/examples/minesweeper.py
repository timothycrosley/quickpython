"""
/games/minesweeper.py

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

import colorama
import pyfiglet

GRID_SIZES = {"easy": 10, "intermediate": 18, "hard": 20}

MINE_COUNTS = {"easy": 10, "intermediate": 50, "hard": 100}

COLORS = [
    colorama.Fore.LIGHTYELLOW_EX,
    colorama.Fore.YELLOW,
    colorama.Fore.LIGHTMAGENTA_EX,
    colorama.Fore.MAGENTA,
    colorama.Fore.LIGHTRED_EX,
    colorama.Fore.RED,
    colorama.Fore.LIGHTCYAN_EX,
    colorama.Fore.CYAN,
]


class Grid:
    def __init__(self, size: int, mine_count: int):
        """
        initializes a `Grid` object
        """

        self.size = size
        self.mine_count = mine_count

        self.known = [[" " for (i) in range(self.size)] for (j) in range(self.size)]

    def get_neighbors(self, cell: tuple) -> set:
        """
        gets a set of surrounding cells from `cell`

        arguments:
            cell     :: tuple :: the cell to surround

        returns:
           neighbors :: set   :: a set of surrounding cells
        """

        row_index, column_index = cell

        neighbors = set()

        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i == 0) and (j == 0):
                    # this is `cell`
                    continue
                elif (-1 < (row_index + i) < self.size) and (-1 < (column_index + j) < self.size):
                    neighbors.add((row_index + i, column_index + j))

        return neighbors

    def get_random_cell(self) -> tuple:
        """
        gets a random (row, column) tuple

        returns:
            :: tuple :: a random (row, column) tuple
        """

        return (random.randint(0, self.size - 1), random.randint(0, self.size - 1))

    def generate_mines(self, start_cell: tuple):
        """
        generates a set of mines excluding `start_cell`

        arguments:
            start_cell :: tuple :: the player's first selected cell
        """

        self.mines = set()
        neighbors = self.get_neighbors(start_cell)

        while len(self.mines) != self.mine_count:
            cell = self.get_random_cell()

            if (cell == start_cell) or (cell in neighbors):
                continue

            self.mines.add(cell)

        for (row, column) in self.mines:
            self.hidden[row][column] = "X"

    def generate_numbers(self):
        """
        generates a number for each cell based on surrounding mines
        """

        for (row_index, row) in enumerate(self.hidden):
            for (column_index, cell) in enumerate(row):
                if cell != "X":
                    values = [
                        self.hidden[row][column]
                        for (row, column) in self.get_neighbors((row_index, column_index))
                    ]
                    number = values.count("X")

                    if number == 0:
                        self.hidden[row_index][column_index] = "0"
                    else:
                        self.hidden[row_index][column_index] = "{0}{1}{2}".format(
                            COLORS[number - 1], number, colorama.Fore.RESET
                        )

    def show(self, grid: list) -> str:
        """
        generates a string containing a readable form of the minesweeper grid

        arguments:
            grid        :: list :: the minesweeper grid to generate

        returns:
            grid_string :: str  :: the readable form of `grid`
        """

        horizontal = "   " + ("-" * (4 * len(grid))) + "-"
        top_label = "     "

        for character in string.ascii_uppercase[: len(grid)]:
            top_label += "{0}   ".format(character)

        grid_string = "{0}\n{1}".format(top_label, horizontal)

        for (i, j) in enumerate(grid, 1):
            row = "\n{0:>2} |".format(i)

            for k in j:
                row += " {0} |".format(k)

            grid_string += "{0}\n{1}".format(row, horizontal)

        return grid_string

    def show_cell(self, cell: tuple):
        """
        sets `cell` in `self.known` as `self.hidden` and iterates through neighbors if `self.known` == "0"

        arguments:
            cell :: tuple :: the cell to show
        """

        row_index, column_index = cell

        if self.known[row_index][column_index] != " ":
            return

        self.known[row_index][column_index] = self.hidden[row_index][column_index]

        if self.known[row_index][column_index] == "0":
            for (row_index, column_index) in self.get_neighbors((row_index, column_index)):
                if self.known[row_index][column_index] != "F":
                    self.show_cell((row_index, column_index))

    def start(self, start_cell: tuple):
        """
        generates the minesweeper grid

        arguments:
            start_cell :: tuple :: passed into `self.generate_mines` and `self.show_cell`
        """

        self.hidden = [["0" for (i) in range(self.size)] for (j) in range(self.size)]

        self.generate_mines(start_cell)
        self.generate_numbers()

        self.show_cell(start_cell)


class Minesweeper:
    def __init__(self, difficulty: str):
        """
        initializes a `Minesweeper` object
        """

        self.grid_size = GRID_SIZES[difficulty]
        self.mine_count = MINE_COUNTS[difficulty]

    def game(self):
        """
        starts the game
        """

        self.grid = Grid(self.grid_size, self.mine_count)
        self.message = ""

        coordinates = ""
        while not self.valid_coordinates(coordinates) or (coordinates.endswith("F")):
            cls()

            print()
            print(self.grid.show(self.grid.known))
            print()

            coordinates = input("coordinates;\n> ").strip().upper()
            if not self.valid_coordinates(coordinates):
                self.message = "invalid coordinates"
                continue

        row, column, flag = self.parse_coordinates(coordinates)

        self.grid.start((row, column))
        flags = set()

        while not flags == self.grid.mines:
            cls()

            print()
            print(self.grid.show(self.grid.known))
            print()

            if self.message:
                print(self.message)
                print()

                self.message = ""
            else:
                print(
                    "{0} mine{1} left".format(
                        len(self.grid.mines) - len(flags),
                        "s" if (len(self.grid.mines) - len(flags) != 1) else "",
                    )
                )
                print()

            coordinates = input("coordinates;\n> ").strip().upper()

            if coordinates.startswith("EVAL("):
                # this entire block of code was me messing with the game and making cheats bc i got bored :))

                # commands are;
                # eval(va-`column``row`) -> sets self.message to the value at `column`, `row`
                # eval(win)              -> does some freaky looking printing to generate mines and win the game

                pattern_string = r"^EVAL\(VA-(?P<column>[A-{0}])(?P<row>{1})\)$".format(
                    string.ascii_uppercase[self.grid_size - 1],
                    "|".join([str(i) for i in range(1, self.grid_size + 1)][::-1]),
                )
                pattern = re.compile(pattern_string)
                match = re.match(pattern, coordinates)

                if match:
                    row = int(match.group("row")) - 1
                    column = string.ascii_uppercase.index(match.group("column"))

                    self.message = self.grid.hidden[row][column]
                    continue

                pattern_string = r"^EVAL\(WIN\)$"
                pattern = re.compile(pattern_string)
                match = re.match(pattern, coordinates)

                if match:
                    for i in range(self.grid_size):
                        for j in range(self.grid_size):
                            if self.grid.known[i][j] != " ":
                                continue

                            if self.grid.hidden[i][j] != "X":
                                continue

                            flags.add((i, j))
                            self.grid.known[i][j] = "F"

                            cls()

                            print()
                            print(self.grid.show(self.grid.known))
                            print()

                            print(
                                "{0} mine{1} left".format(
                                    len(self.grid.mines) - len(flags),
                                    "s" if (len(self.grid.mines) - len(flags) != 1) else "",
                                )
                            )

                    continue

            if not self.valid_coordinates(coordinates):
                self.message = "invalid coordinates"
                continue

            row, column, flag = self.parse_coordinates(coordinates)

            if flag:
                if self.grid.known[row][column] == " ":
                    self.grid.known[row][column] = "F"
                    flags.add((row, column))
                elif self.grid.known[row][column] == "F":
                    self.grid.known[row][column] = " "
                    flags.remove((row, column))
                else:
                    self.message = "cannot put a flag there"
            elif (row, column) in flags:
                self.message = "there is a flag there"
            elif self.grid.hidden[row][column] == "X":
                cls()

                print()
                print(self.grid.show(self.grid.hidden))
                print()
                print("you lose")

                return
            elif self.grid.known[row][column] == " ":
                self.grid.show_cell((row, column))
            else:
                self.message = "that cell is already shown"

        cls()

        print()
        print(self.grid.show(self.grid.hidden))
        print()
        print("you win")

    def parse_coordinates(self, coordinates: str) -> tuple:
        """
        generates a (row : int, column : int, flag : bool) tuple from coordinates

        arguments:
            coordinates :: str   :: the coordinates convert

        returns:
                        :: tuple :: a (row : int, column : int, flag : bool) tuple
        """

        pattern = re.compile(
            r"^(?P<column>[A-{0}])(?P<row>{1})(?P<flag>F?)$".format(
                string.ascii_uppercase[self.grid_size - 1],
                "|".join([str(i) for i in range(1, self.grid_size + 1)][::-1]),
            )
        )
        match = re.match(pattern, coordinates)

        row = int(match.group("row")) - 1
        column = string.ascii_uppercase.index(match.group("column"))
        flag = match.group("flag") == "F"

        return (row, column, flag)

    def start(self):
        """
        calls `self.game` in a 'would you like to play again?' loop
        """

        choice = "y"
        while choice.startswith("y"):
            cls()
            print(pyfiglet.figlet_format("Minesweeper"))
            print()
            input("enter to play\nctrl + c to quit to main menu\n\n")

            self.game()
            choice = input("\nwould you like to play again?\n> ").strip()

    def valid_coordinates(self, coordinates: str) -> bool:
        """
        determines whether `coordinates` are valid

        arguments:
            coordinates :: str  :: the coordinates to check

        returns:
                        :: bool :: whether `coordinates` are valid
        """

        pattern = re.compile(
            r"^(?P<column>[A-{0}])(?P<row>{1})(?P<flag>F?)$".format(
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

    game = Minesweeper(difficulty)
    game.start()
