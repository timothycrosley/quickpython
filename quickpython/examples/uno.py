"""
/games/uno.py

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

__version_info__ = (2, 0, 0, "final", 0)
__version__ = "{0}.{1}.{2}{3}{4}".format(
    *[str(n)[0] if (i == 3) else str(n) for (i, n) in enumerate(__version_info__)]
)


import os
import random

import colorama
import pyfiglet

CARD_COLORS = ["Blue", "Green", "Red", "Yellow"]

CARD_NAMES = [
    "0",
    "1",
    "1",
    "2",
    "2",
    "3",
    "3",
    "4",
    "4",
    "5",
    "5",
    "6",
    "6",
    "7",
    "7",
    "8",
    "8",
    "9",
    "9",
    "Reverse",
    "Skip",
    "+2",
]

START_HAND = 7

COLOR_FORMATS = {
    "Blue": colorama.Fore.BLUE,
    "Green": colorama.Fore.GREEN,
    "Red": colorama.Fore.RED,
    "Yellow": colorama.Fore.YELLOW,
}


class Card:
    def __init__(self, color: str, name: str):
        """
        initializes a `Card` object
        """

        self.color = color
        self.name = name

    def format(self) -> str:
        """
        formats the card with cli color codes

        returns:
            :: str :: the formatted card
        """

        if self.color != "Wild":
            return "{}{}{}".format(COLOR_FORMATS[self.color], self.short_name, colorama.Fore.RESET)
        return self.short_name

    def is_wild(self) -> bool:
        """
        checks whether the `Card` object is a wildcard

        returns:
            :: bool :: whether the `Card` object is a wildcard
        """

        if self.color == "Wild":
            return True
        return False

    @property
    def short_name(self) -> str:
        """
        generates a short name for the `Card` object

        returns:
            :: str :: the `Card` object's short name
        """

        return "{}{}".format(self.color[:1:], self.name[:1:])


class Deck:
    def __init__(self):
        """
        initializes a `Deck` object
        """

        self.deck = list()
        self.in_play = list()
        self.in_pile = list()

        # add color cards
        for color in CARD_COLORS:
            for name in CARD_NAMES:
                self.deck.append(Card(color, name))

        # add wildcards
        for i in range(4):
            for name in ["Change", "+4"]:
                self.deck.append(Card("Wild", name))

        self.shuffle()

    def flip(self):
        """
        flips `self.in_pile` back over into `self.deck`
        """

        if not self.deck:
            self.deck = self.in_pile
            self.in_pile = list()

    def is_empty(self) -> bool:
        """
        checks whether `self.deck` is empty

        returns:
            :: bool :: whether `self.deck` is empty
        """

        if len(self.deck) == 0:
            return True
        return False

    def reset(self):
        """
        re-builds `self.deck`, `self.in_play` and `self.in_pile` and calls `self.shuffle`
        """

        self.deck = list()
        self.in_play = list()
        self.in_pile = list()

        for color in CARD_COLORS:
            for name in CARD_NAMES:
                self.deck.append(Card(color, name))

        for i in range(4):
            for name in ["Change", "+4"]:
                self.deck.append(Card("Wild", name))

        self.shuffle()

    def shuffle(self):
        """
        shuffles `self.deck`
        """

        random.shuffle(self.deck)


class Hand:
    def __init__(self, deck: Deck):
        """
        initializes a `Hand` object
        """

        self.deck = deck
        self.hand = list()

    def __len__(self) -> int:
        """
        utilized by built-in `len` function
        """

        return len(self.hand)

    def generate(self):
        """
        fills `self.hand` up to len( `START_HAND` )
        """

        for i in range(START_HAND):
            card = self.deck.deck.pop()
            self.hand.append(card)
            self.deck.in_play.append(card)

    def reset(self):
        """
        sets `self.hand` to an empty list
        """

        self.hand = list()


class Player:
    def __init__(self, name: str, deck: Deck):
        """
        initializes a `Player` object
        """

        self.name = name
        self.deck = deck

        self.hand = Hand(self.deck)

    def is_winner(self) -> bool:
        """
        checks whether the `Player` has won the game

        returns:
            :: bool :: whether the `Player` has won the game
        """

        if len(self.hand) == 0:
            return True
        return False


class Uno:
    def __init__(self, player_count: int):
        """
        initializes an `Uno` object
        """

        self.player_count = player_count

    def game(self):
        """
        starts the game
        """

        self.deck = Deck()
        self.players = list()

        self.current_player = 0
        self.clockwise = True

        self.message = ""
        self.color = None

        for i in range(self.player_count):
            self.players.append(Player("P{}".format(i + 1), self.deck))
            self.players[i].hand.generate()

        card = self.deck.deck.pop()
        self.top_card = card
        self.deck.in_pile.append(card)

        if len(self.players) == 2:
            players = [self.players[0].name, self.players[1].name, "--", "--"]
        elif len(self.players) == 3:
            players = [
                self.players[0].name,
                self.players[1].name,
                self.players[2].name,
                "--",
            ]
        elif len(self.players) == 4:
            players = [
                self.players[0].name,
                self.players[1].name,
                self.players[2].name,
                self.players[3].name,
            ]

        while not any([player.is_winner() for player in self.players]):
            cls()

            if self.color:
                color = COLOR_FORMATS[self.color]
            else:
                color = ""

            if self.current_player == 0:
                pointers = ["/\\", " ", " ", " "]
            elif self.current_player == 1:
                pointers = [" ", ">", " ", " "]
            elif self.current_player == 2:
                pointers = [" ", " ", "\\/", " "]
            elif self.current_player == 3:
                pointers = [" ", " ", " ", "<"]

            print(
                """
            {4} left in deck
            
                     {0}
                     {8}
            
            {3} {11}     {5}{6}{7}     {9} {1}
            
                     {10}
                     {2}
            """.format(
                    *players,
                    len(self.deck.deck),
                    color,
                    self.top_card.format(),
                    colorama.Fore.RESET,
                    *pointers
                )
            )

            print()

            if self.message:
                print(self.message)
                print()

                self.message = ""

            print(self.players[self.current_player].name)

            for card in self.players[self.current_player].hand.hand:
                print(card.format(), end=" ")

            print()
            print()

            card = input("choose a card to place;\n> ").strip().upper()

            if card == "+":
                if self.deck.is_empty():
                    self.deck.flip()

                card = self.deck.deck.pop()
                self.players[self.current_player].hand.hand.append(card)
                self.deck.in_play.append(card)
                continue

            try:
                card_index = int(card)

                if card_index not in range(1, len(self.players[self.current_player].hand.hand) + 1):
                    self.message = (
                        "card must be an integer in range 1 - {0} or the card name".format(
                            len(self.players[self.current_player].hand.hand)
                        )
                    )
                    continue

                card = self.players[self.current_player].hand.hand[card_index - 1]
            except (ValueError) as e:
                if card not in [
                    card.short_name for card in self.players[self.current_player].hand.hand
                ]:
                    self.message = (
                        "card must be an integer in range 1 - {0} or the card name".format(
                            len(self.players[self.current_player].hand.hand)
                        )
                    )
                    continue

                card = self.players[self.current_player].hand.hand[
                    [card.short_name for card in self.players[self.current_player].hand.hand].index(
                        card
                    )
                ]

            if card.color == "Wild":
                pass
            elif self.top_card.color == "Wild":
                if card.color != self.color:
                    self.message = "you can't place that card"
                    continue
            elif card.color == self.top_card.color:
                pass
            elif card.name == self.top_card.name:
                pass
            else:
                self.message = "you can't place that card"
                continue

            card = self.players[self.current_player].hand.hand.pop(
                self.players[self.current_player].hand.hand.index(card)
            )
            self.top_card = card
            self.deck.in_play.remove(card)
            self.deck.in_pile.append(card)

            add_cards = 0
            skip_player = False
            reverse = False

            color = ""

            if self.top_card.name == "Change":
                self.color = ""
                while self.color not in ["Blue", "Green", "Red", "Yellow"]:
                    cls()

                    print(
                        """
            {4} left in deck
            
                     {0}
                     {8}
            
            {3} {11}     {5}{6}{7}     {9} {1}
            
                     {10}
                     {2}
                    """.format(
                            *players,
                            len(self.deck.deck),
                            color,
                            self.top_card.format(),
                            colorama.Fore.RESET,
                            *pointers
                        )
                    )

                    print()

                    if self.message:
                        print(self.message)
                        print()

                        self.message = ""

                    print(self.players[self.current_player].name)

                    for card in self.players[self.current_player].hand.hand:
                        print(card.format(), end=" ")

                    print()
                    print()

                    self.color = input("choose a color;\n> ").strip().capitalize()
            elif self.top_card.name == "+4":
                self.color = ""
                while self.color not in ["Blue", "Green", "Red", "Yellow"]:
                    cls()

                    print(
                        """
            {4} left in deck
            
                     {0}
                     {8}
            
            {3} {11}     {5}{6}{7}     {9} {1}
            
                     {10}
                     {2}
                    """.format(
                            *players,
                            len(self.deck.deck),
                            color,
                            self.top_card.format(),
                            colorama.Fore.RESET,
                            *pointers
                        )
                    )

                    print()

                    if self.message:
                        print(self.message)
                        print()

                        self.message = ""

                    print(self.players[self.current_player].name)

                    for card in self.players[self.current_player].hand.hand:
                        print(card.format(), end=" ")

                    print()
                    print()

                    self.color = input("choose a color;\n> ").strip().capitalize()

                add_cards = 4
                skip_player = True
            elif self.top_card.name == "+2":
                add_cards = 2
                skip_player = True
            elif self.top_card.name == "Skip":
                skip_player = True
            elif self.top_card.name == "Reverse":
                reverse = True

            if reverse:
                self.clockwise = not self.clockwise

                if len(self.players) == 2:
                    # we don't want to change the player
                    continue

            if self.clockwise:
                next_player = self.current_player + 1
            else:
                next_player = self.current_player - 1

            if next_player > (len(self.players) - 1):
                next_player -= len(self.players)
            elif next_player < 0:
                next_player += len(self.players)

            if add_cards:
                for i in range(add_cards):
                    if self.deck.is_empty():
                        self.deck.flip()

                    card = self.deck.deck.pop()
                    self.players[next_player].hand.hand.append(card)
                    self.deck.in_play.append(card)

            if skip_player:
                if self.clockwise:
                    next_player = self.current_player + 2
                else:
                    next_player = self.current_player - 2

                if next_player > (len(self.players) - 1):
                    next_player -= len(self.players)
                elif next_player < 0:
                    next_player += len(self.players)

            self.current_player = next_player

        winner = [player for player in self.players if player.is_winner()][0]

        cls()

        print()
        print(
            """
            {4} left in deck
            
                     {0}
                     {8}
            
            {3} {11}     {5}{6}{7}     {9} {1}
            
                     {10}
                     {2}
        """.format(
                *players,
                len(self.deck.deck),
                color,
                self.top_card.format(),
                colorama.Fore.RESET,
                *pointers
            )
        )

        print()
        print("{0} wins!".format(winner.name))

    def start(self):
        """
        calls `self.game` in a 'would you like to play again?' loop
        """

        choice = "y"
        while choice.startswith("y"):
            cls()
            print(pyfiglet.figlet_format("Uno"))
            print()
            input("enter to play\nctrl + c to quit to main menu\n\n")

            self.game()
            choice = input("\nwould you like to play again?\n> ").strip()


if __name__ == "__main__":
    players = None
    while not isinstance(players, int):
        cls()
        players = input("players;\n> ")

        try:
            players = int(players)
        except (ValueError) as e:
            pass

    game = Uno(players)
    game.start()
