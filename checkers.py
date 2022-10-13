"""Assignment 2 Game Tree Search"""
import math
import sys
from heapq import heappush, heappop
from dataclasses import dataclass, field
from typing import Any


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
        # self.red = {(7, 2): 'R', (7, 4): 'r', (3, 6): 'r'}
        # self.black = {(4, 1): 'b', (2,  3): 'b', (4, 3): 'b', (3, 4): 'b', (4, 7): 'B'}
        self.red = dict()
        self.black = dict()

    def __str__(self) -> str:
        """
        Print the state information to console.
        """
        # initialize the board info
        lst = []
        result = ''
        for _ in range(8):
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

    def move(self, position: tuple, destination: tuple):
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
            # print("ERROR: not eligible diagonal move.")
            return None

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
            return destination

        # Red piece capture a black piece or nothing happen
        # if there are no empty space across black piece
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
                return new_des

        # Black piece capture a red piece or nothing happen
        # if there are no empty space across red piece
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
                return new_des
        # else:
        #     print("ERROR: not eligible move: same color in position and destination")
        return None


def terminal(state: State) -> bool:
    """Return True if any player in play win."""
    # Check whether any player in play has no pieces.
    if len(state.red) == 0 or len(state.black) == 0:
        return True
    # Check whether any player in play cannot make a eligible move:
    if len(expand(state, 'r')) == 0 or len(expand(state, 'b')) == 0:
        return True
    return False


def txt_to_state(file: str) -> State:
    """Return a State that convert input form to a game board state."""
    f = open(file, 'r')
    str_lst = f.readlines()
    result = State()
    for y in range(8):
        for x in range(8):
            if str_lst[y][x] == 'r':
                result.red[(x, y)] = 'r'
            elif str_lst[y][x] == 'R':
                result.red[(x, y)] = 'R'
            elif str_lst[y][x] == 'b':
                result.black[(x, y)] = 'b'
            elif str_lst[y][x] == 'B':
                result.black[(x, y)] = 'B'
    return result


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
            s1_lst = expand_single(s1, key, 'r')
            s2_lst = expand_single(s2, key, 'r')
            s3_lst = expand_single(s3, key, 'r')
            s4_lst = expand_single(s4, key, 'r')
            for i in [s1_lst, s2_lst, s3_lst, s4_lst]:
                for s in i:
                    if s != state and s not in result:
                        result.append(s)
    else:
        for key in state.black:
            # Clone 4 states for movement
            s1 = clone(state)
            s2 = clone(state)
            s3 = clone(state)
            s4 = clone(state)
            s1_lst = expand_single(s1, key, 'b')
            s2_lst = expand_single(s2, key, 'b')
            s3_lst = expand_single(s3, key, 'b')
            s4_lst = expand_single(s4, key, 'b')
            for i in [s1_lst, s2_lst, s3_lst, s4_lst]:
                for s in i:
                    if s != state and s not in result:
                        result.append(s)
    return result


def expand_single(state: State, position: tuple, player: str) -> list[State]:
    """
    Return a list of State by a given position of piece.
    Assume the space at position is not empty.
    """
    result = []
    des_lst = []
    if player == 'r':
        assert position in state.red
        # List out all the possible destination
        if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] - 1) <= 7:
            des_lst.append((position[0] - 1, position[1] - 1))
        if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] - 1) <= 7:
            des_lst.append((position[0] + 1, position[1] - 1))

        if state.red[position] == 'R':
            if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] + 1) <= 7:
                des_lst.append((position[0] - 1, position[1] + 1))
            if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] + 1) <= 7:
                des_lst.append((position[0] + 1, position[1] + 1))

        # Get all possible state and multiple capture state by using multi_jump.
        for des in des_lst:
            nxt_state = clone(state)
            curr_position = nxt_state.move(position, des)
            # Filter out the des that is/are not eligible move
            if nxt_state != state:
                if des != curr_position:  # it means that the player had
                                          # capture his/her opponent's piece

                    if state.red[position] != nxt_state.red[curr_position]:
                        # Situation when the piece on curr_position promote to a King.
                        if nxt_state not in result:
                            result.append(nxt_state)
                    else:
                        multi_return = multi_jump(nxt_state, curr_position,
                                                  get_surr(nxt_state, curr_position, player),
                                                  player, nxt_state.red[curr_position])
                        for s in multi_return:
                            if s not in result:
                                result.append(s)
                else:
                    if nxt_state not in result:
                        result.append(nxt_state)
    # For the black player
    else:
        assert position in state.black
        # List out all the possible destination
        if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] + 1) <= 7:
            des_lst.append((position[0] - 1, position[1] + 1))
        if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] + 1) <= 7:
            des_lst.append((position[0] + 1, position[1] + 1))

        if state.black[position] == 'B':
            if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] - 1) <= 7:
                des_lst.append((position[0] - 1, position[1] - 1))
            if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] - 1) <= 7:
                des_lst.append((position[0] + 1, position[1] - 1))

        # Get all possible state and multiple capture state by using multi_jump.
        for des in des_lst:
            nxt_state = clone(state)
            curr_position = nxt_state.move(position, des)
            # Filter out the des that is/are not eligible move
            if nxt_state != state:
                if des != curr_position:  # it means that the player had
                                          # capture his/her opponent's piece
                    if state.black[position] != nxt_state.black[curr_position]:
                        # Situation when the piece on curr_position promote to a King.
                        if nxt_state not in result:
                            result.append(nxt_state)
                    else:
                        multi_return = multi_jump(nxt_state, curr_position,
                                                  get_surr(nxt_state, curr_position, player),
                                                  player, nxt_state.black[curr_position])
                        for s in multi_return:
                            if s not in result:
                                result.append(s)
                else:
                    if nxt_state not in result:
                        result.append(nxt_state)
    return result


def multi_jump(state: State, position: tuple,
               surr: list[tuple], player: str, piece: str) -> list[State]:
    """Helper function for expand_single that check surrounding
    diagonal space of position and find where can do a multiple jump"""
    result = []
    if surr == []:
        return [state]
    else:
        for neighbour in surr:
            nxt_state = clone(state)
            curr_pos = nxt_state.move(position, neighbour)
            if state != nxt_state:
                # Is piece at curr_pos become King?
                if (piece == 'r' and curr_pos[1] == 0) or (piece == 'b' and curr_pos[1] == 7):
                    # Turn ends
                    if nxt_state not in result:
                        result.append(nxt_state)
                else:
                    # Recursion for getting the final state of multiple capture
                    multi_return = multi_jump(nxt_state, curr_pos,
                                              get_surr(nxt_state, curr_pos, player), player, piece)
                    for s in multi_return:
                        if s not in result:
                            result.append(s)
            else:
                if nxt_state not in result:
                    result.append(nxt_state)
        return result


def get_surr(state: State, position: tuple, player: str):
    """Helper function for getting position of opponent's piece on the adjacent diagonal space."""
    result = []
    if player == 'r':
        if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] - 1) <= 7 and \
                (position[0] - 1, position[1] - 1) in state.black:
            result.append((position[0] - 1, position[1] - 1))
        if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] - 1) <= 7 and \
                (position[0] + 1, position[1] - 1) in state.black:
            result.append((position[0] + 1, position[1] - 1))

        if state.red[position] == 'R':
            if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] + 1) <= 7 and \
                    (position[0] - 1, position[1] + 1) in state.black:
                result.append((position[0] - 1, position[1] + 1))
            if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] + 1) <= 7 and \
                    (position[0] + 1, position[1] + 1) in state.black:
                result.append((position[0] + 1, position[1] + 1))
    else:
        if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] + 1) <= 7 and \
                (position[0] - 1, position[1] + 1) in state.red:
            result.append((position[0] - 1, position[1] + 1))
        if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] + 1) <= 7 and \
                (position[0] + 1, position[1] + 1) in state.red:
            result.append((position[0] + 1, position[1] + 1))

        if state.black[position] == 'B':
            if 0 <= (position[0] - 1) <= 7 and 0 <= (position[1] - 1) <= 7 and \
                    (position[0] - 1, position[1] - 1) in state.red:
                result.append((position[0] - 1, position[1] - 1))
            if 0 <= (position[0] + 1) <= 7 and 0 <= (position[1] - 1) <= 7 and \
                    (position[0] + 1, position[1] - 1) in state.red:
                result.append((position[0] + 1, position[1] - 1))
    return result


def clone(state: State) -> State:
    """Return a same State without aliasing"""
    c = State()
    for key in state.red:
        c.red[key] = state.red[key]
    for key in state.black:
        c.black[key] = state.black[key]
    return c


def utility(state: State) -> int:
    """
    Return a int calculate by utility function.
    Calculation:
        - Each red man piece worth 1 point and King worth 2 points
        - Each black man piece worth -1 point and King worth -2 points
        - Each piece of black piece that cannot move +2 points
        - Each piece of red piece that cannot move -2 points
    """
    value = 0
    for key in state.red:
        if state.red[key] == 'r':
            value += 1
        else:
            value += 2
    for key in state.black:
        if state.black[key] == 'b':
            value -= 1
        else:
            value -= 2
    return value


def heuristic(state: State) -> int:
    """
    Advanced heuristic function for calculating the trade-off value of a given EXPANDED state.
    Calculation:
        - Each red man piece worth 1 point and King worth 2 points
        - Each black man piece worth -1 point and King worth -2 points
        - Each piece of black piece that cannot move +2 points
        - Each piece of red piece that cannot move -2 points
        - If any piece of player may be captured in next expand
          +/- 1 point for each man and +/- 3 points for each King (not implemented)
    """
    value = 0
    for key in state.red:
        if state.red[key] == 'r':
            value += 1
        else:
            value += 2
        # Does that piece able to move?
        if len(expand_single(state, key, 'r')) == 0:
            value -= 2

    for key in state.black:
        if state.black[key] == 'b':
            value -= 1
        else:
            value -= 2
        # Does that piece able to move?
        if len(expand_single(state, key, 'b')) == 0:
            value += 2

    return value


def ab_search(state: State, d_limit: int) -> State:
    """Minimax search with alpha-beta pruning"""
    best_move, _ = max_value(state, -math.inf, math.inf, d_limit)
    return best_move


def max_value(state: State, a: float, b: float, d_limit: int):
    """Minimax function for finding max node"""
    best_move = None
    if terminal(state):
        return best_move, utility(state)
    elif d_limit == 0:
        return best_move, heuristic(state)
    value = -math.inf
    # Rearrange the list of expanded state by
    # the heuristic value by descending
    # (index 0 is largest ont and the last index is the smallest one)
    ex_lst = expand(state, 'r')
    ex_lst = rearrange(ex_lst, True)
    for successor in ex_lst:
        _, nxt_v = min_value(successor, a, b, d_limit - 1)
        if value < nxt_v:
            value = nxt_v
            best_move = successor
        # alpha-beta pruning
        if value >= b:
            return best_move, value
        a = max(a, value)
    return best_move, value


def min_value(state: State, a: float, b: float, d_limit: int):
    """Minimax function for finding min """
    best_move = None
    if terminal(state) or d_limit == 0:
        return best_move, utility(state)
    value = math.inf
    # Rearrange the list of expanded state by
    # the heuristic value by ascending
    # (index 0 is smallest ont and the last index is the largest one)
    ex_lst = expand(state, 'b')
    ex_lst = rearrange(ex_lst, False)
    for successor in ex_lst:
        _, nxt_v = max_value(successor, a, b, d_limit - 1)
        if value > nxt_v:
            value = nxt_v
            best_move = successor
        # alpha-beta pruning
        if value <= a:
            return best_move, value
        b = min(b, value)
    return best_move, value


def rearrange(ex_lst: list[State], reverse: bool) -> list[State]:
    """
    Helper function for rearranging state by the heuristic value
    by descending index 0 is largest ont and
    the last index is the smallest one.
    param:
     - ex_lst: A list of expanded state.
     - reverse: False means return a list ordered by ascending;
                True means return a list ordered by descending.
    """
    return sorted(ex_lst, key=heuristic, reverse=reverse)


if __name__ == '__main__':
    state1 = State()
    print(state1)
    state2 = clone(state1)
    state2.black = {(7, 6): 'b'}
    state2.red = {(6, 7): 'R'}
    state3 = clone(state1)
    state3.black = {(1, 3): 'b'}
    state3.red = {(0, 6): 'r', (2, 6): 'r', (4, 6): 'r', (6, 6): 'r', (2, 4): 'r'}

    print(heuristic(state2), heuristic(state3))
    # surr = get_surr(state2, (3, 4), 'r')
    # test_lst = expand(state2, 'b')
    # bol = terminal(state2)
