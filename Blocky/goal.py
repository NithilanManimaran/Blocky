"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple, Optional
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    typ = random.randint(0, 1)
    x = []
    clr_lst = COLOUR_LIST[:]
    if typ == 0:
        for _ in range(num_goals):
            clr = random.choice(clr_lst)
            x.append(PerimeterGoal(clr))
            clr_lst.remove(clr)
        return x
    else:
        for _ in range(num_goals):
            clr = random.choice(clr_lst)
            x.append(BlobGoal(clr))
            clr_lst.remove(clr)
        return x


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    lst = []
    unit_s = block.size / (2 ** block.max_depth)
    for i in range(2 ** block.max_depth):
        lst.append([])
        for j in range(2 ** block.max_depth):
            lst[i].append(find_colour(block, (
                block.position[0] + i*unit_s + unit_s/2,
                unit_s/2+j * unit_s+block.position[1])))
    return lst


def find_colour(block: Block, x: Tuple[int, int]) -> Optional[Tuple[int,
                                                                    int, int]]:
    """Return the colour of <block> at position <x>.
    """
    if block.colour is not None:
        pos = block.position
        if pos[0] < x[0] < pos[0] + block.size and \
                pos[1] < x[1] < pos[1] + block.size:
            return block.colour
        else:
            return None
    else:
        for item in block.children:
            col = find_colour(item, x)
            if col is not None:
                return col
    return None


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A perimeter goal.
    """
    def score(self, board: Block) -> int:
        """Return the current score for a Perimeter Goal scoring on the given
        board.

        The score is always greater than or equal to 0.
        """
        bo_2d = _flatten(board)
        count = 0
        for i in range(len(bo_2d)):
            if i in (0, len(bo_2d) - 1):
                count += bo_2d[i].count(self.colour)
            if bo_2d[i][0] == self.colour:
                count += 1
            if bo_2d[i][len(bo_2d) - 1] == self.colour:
                count += 1
        return count

    def description(self) -> str:
        """Return a description of Perimeter Goal.
        """
        return 'Perimeter Goal: Win by putting the most possible {0} units ' \
               'on the outer perimeter of the board.'\
            .format(colour_name(self.colour))


class BlobGoal(Goal):
    """A blob goal.
    """
    def score(self, board: Block) -> int:
        """Return the current score for a Blob Goal scoring on the given
        board.

        The score is always greater than or equal to 0.
        """
        bo_2d = _flatten(board)
        visited = []
        for i in range(len(bo_2d)):
            visited.append([-1] * len(bo_2d))
        blob_sizes = []
        for i in range(len(visited)):
            for j in range(len(visited)):
                if visited[i][j] == -1:
                    blob_sizes.append(self._undiscovered_blob_size(
                        (i, j), bo_2d, visited))
        return max(blob_sizes)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        x, y = pos
        if x < 0 or x >= len(board) or y >= len(board) or y < 0:
            return 0
        # Check if cell has been visited
        if visited[x][y] != -1:
            return 0
        elif board[x][y] != self.colour:
            visited[x][y] = 0
            return 0
        else:
            # Since we know the cell is unvisited and is of the target colour
            visited[x][y] = 1
            size = 1
            for i in range(4):
                if i == 0:
                    c = (x, y - 1)
                elif i == 1:
                    c = (x - 1, y)
                elif i == 2:
                    c = (x, y + 1)
                else:
                    c = (x + 1, y)
                size += self._undiscovered_blob_size(c, board, visited)

            return size

    def description(self) -> str:
        """Return a description of Blob Goal.
        """
        return 'Blob Goal: Win by connecting the most {0} blocks (side by ' \
               'side) to each other.'.format(colour_name(self.colour))


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
