"""Assignment 2 Game Tree Search"""
# import sys
# from heapq import heappush, heappop
# from dataclasses import dataclass, field
# from typing import Any


class State:
    """
    This class record a state of board in dictionary.

    Attributes:
    map: A dictionary stores the position of each space (treat it as coordinates) as key and
    the corresponding value of each key is a list.
    In the list, we store the type of piece as string at index 0 ('r' is a red piece;
    'R' is a red king; 'b' is a black piece; 'B' is a black king; '.' means no piece on it),
    and index 1 stores what color is that space (0 is white;
    1 is black which only black can be occupied by a piece).

    red/black: A dictionary stores the position of red/black pieces on the board
    (position stores in coordinates form) as key,
    and the corresponding value of each key is a string ('r' is a red piece;
    'R' is a red king; 'b' is a black piece; 'B' is a black king).
    NOTE: Domain of coordinates: {(x, y)| 0 <= x <= 7, 0 <= y <= 7}.

    Method:
    - move(position: tuple, destination: tuple):
        Move the piece on the given position to destination position
        NOTE: assume we move right color piece every move, and the position is not empty.
    - display():
        print the state information (where is each piece at) as "matrix-like" form to console.

    """
    # map: dict[tuple, list[str, int]]
    red: dict[tuple, str]
    black: dict[tuple, str]

    def __init__(self) -> None:
        self.red = {(7, 2): 'R', (7, 4): 'r', (3, 6): 'r'}
        self.black = {(4, 1): 'b', (2,  3): 'b', (4, 3): 'b', (3, 4): 'b', (4, 7): 'B'}

    def __str__(self) -> str:
        """
        Print the state information to console.
        """
        # initialize the board info
        lst = []
        result = ''
        for i in range(8):
            lst.append(['.', '.', '.', '.', '.', '.', '.', '.'])

        for key in self.black:
            lst[key[1]][key[0]] = self.black[key]

        for key in self.red:
            lst[key[1]][key[0]] = self.red[key]

        for i in range(8):
            result += ''.join(lst[i])
            result += '\n'

        return result

    def __eq__(self, other):
        """
        Return True if all items in other's red and black are same as self's
        """
        # Check whether they have same number of elements in red and black map
        if len(self.red) != len(other.red) \
                or len(self.black) != len(other.black):
            return False

        # Check all key and the corresponding value of that key are
        # same in self's and other's red and black map
        for key in self.red:
            if key not in other.red:
                return False
            elif self.red[key] != other.red[key]:
                return False
        for key in self.black:
            if key not in other.black:
                return False
            elif self.black[key] != other.black[key]:
                return False
        return True

    def move(self, position: tuple, destination: tuple) -> None:
        """
        Move the piece on the given position to destination position.
        Destination should be diagonal one space forward or backward.
        Assume player move eligible piece and follow the rule of move.
        NOTE: assume we move right color piece every move, and the position is not empty.
        NOTE: We include jump in move().
        """
        assert position in self.red or position in self.black
        assert 0 <= position[0] <= 7
        assert 0 <= position[1] <= 7
        assert 0 <= destination[0] <= 7
        assert 0 <= destination[1] <= 7
        # Check eligibility
        # - diagonally move
        x_dis = destination[0] - position[0]
        y_dis = destination[1] - position[1]
        if abs(x_dis) != 1 or abs(y_dis) != 1:
            print("ERROR: not eligible diagonal move.")
            return

        if (destination not in self.red) and (destination not in self.black):
            # destination is empty, then move piece in position to destination
            if position in self.red:
                piece = self.red.pop(position)
                if destination[1] == 0:
                    self.red[destination] = 'R'
                else:
                    self.red[destination] = piece
            else:
                piece = self.black.pop(position)
                if destination[1] == 7:
                    self.black[destination] = 'B'
                else:
                    self.black[destination] = piece
            return

        if position in self.red and destination in self.black:
            new_des = (destination[0] + x_dis, destination[1] + y_dis)
            if 0 <= new_des[0] <= 7 and 0 <= new_des[1] <= 7 \
                    and new_des not in self.black and new_des not in self.red:
                # jump to the space that across destination
                piece = self.red.pop(position)
                if new_des[1] == 0:
                    self.red[new_des] = 'R'
                else:
                    self.red[new_des] = piece
                # remove the piece on destination
                self.black.pop(destination)

        elif position in self.black and destination in self.red:
            new_des = (destination[0] + x_dis, destination[1] + y_dis)
            if 0 <= new_des[0] <= 7 and 0 <= new_des[1] <= 7 \
                    and new_des not in self.black and new_des not in self.red:
                # jump to the space that across destination
                piece = self.black.pop(position)
                if new_des[1] == 7:
                    self.black[new_des] = 'B'
                else:
                    self.black[new_des] = piece
                # remove the piece on destination
                self.red.pop(destination)
        else:
            print("ERROR: not eligible move: same color in position and destination")
        return


def expand(state: State, player: str) -> list[State]:
    """
    Return all the possible successor of state.
    Assume the input of player is either 'r' or 'b' ('r' for red, 'b' for black).
    """
    result = []
    if player == 'r':
        for key in state.red:
            # Clone 4 states for movement
            s1 = clone(state)
            s2 = clone(state)
            s3 = clone(state)
            s4 = clone(state)
            if state.red[key] == 'r':
                # man can only move forward
                s1.move(key, (key[0] + 1, key[1] - 1))
                s2.move(key, (key[0] - 1, key[1] - 1))
                for i in [s1, s2]:
                    if i != state and i not in result:
                        result.append(i)
            else:
                # King can move forward and backward
                s1.move(key, (key[0] + 1, key[1] - 1))
                s2.move(key, (key[0] - 1, key[1] - 1))
                s3.move(key, (key[0] + 1, key[1] + 1))
                s4.move(key, (key[0] - 1, key[1] + 1))
                for i in [s1, s2, s3, s4]:
                    if i != state and i not in result:
                        result.append(i)
    else:
        for key in state.black:
            # Clone 4 states for movement
            s1 = clone(state)
            s2 = clone(state)
            s3 = clone(state)
            s4 = clone(state)
            if state.black[key] == 'b':
                # man can only move forward
                s1.move(key, (key[0] + 1, key[1] + 1))
                s2.move(key, (key[0] - 1, key[1] + 1))
                for i in [s1, s2]:
                    if i != state and i not in result:
                        result.append(i)
            else:
                # King can move forward and backward
                s1.move(key, (key[0] + 1, key[1] - 1))
                s2.move(key, (key[0] - 1, key[1] - 1))
                s3.move(key, (key[0] + 1, key[1] + 1))
                s4.move(key, (key[0] - 1, key[1] + 1))
                for i in [s1, s2, s3, s4]:
                    if i != state and i not in result:
                        result.append(i)
    return result


def clone(state: State) -> State:
    """Return a same State without aliasing"""
    c = State()
    for key in state.red:
        c.red[key] = state.red[key]
    for key in state.black:
        c.black[key] = state.black[key]
    return c


def utility(state: State, player: str) -> int:
    """Return a int calculate by utility function."""
    # TODO: Implement utility function


if __name__ == '__main__':
    s = State()
    print(s)
