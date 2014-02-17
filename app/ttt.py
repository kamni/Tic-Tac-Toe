"""
Functions and classes for playing the game. The UI classes can be found in
run.py
"""
import re


class TicTacToeBoard(object):
    """
    Primary class for tracking and playing the game.  
    
    Each of the nine squares on the board is represented by a number, like so:
                    ___________
                   | 8 | 7 | 6 |
                    -----------
                   | 1 | 0 | 5 |
                    -----------
                   | 2 | 3 | 4 |
                    -----------
    
    These numbers directly correspond to positions in the binary representation
    of the board. An empty board would be represented in binary as:
    
             [8]  [7]  [6]  [5]  [4]  [3]  [2]  [1]  [0]
             0 0  0 0  0 0  0 0  0 0  0 0  0 0  0 0  0 0
             
    The first bit of the two-bit representation of a square indicates whether
    or not the position is filled. The second bit represents either an 'X' (1)
    or an 'O' (0). For example:
                    ___________
                   | X |   |   |
                    -----------
                   |   | O | O |
                    -----------
                   |   | X |   |
                    -----------
    
    This board can be represented in binary as:
       
             [8]  [7]  [6]  [5]  [4]  [3]  [2]  [1]  [0]
             1 1  0 0  0 0  1 0  0 0  1 1  0 0  0 0  1 0
             
    This value is stored as a hex value to make it shorter, so this board would 
    be represented as 0x3080c2.
    """
    def __init__(self):
        """
        Sets the default attributes for the class. No parameters are accepted.
        
        :attr board: an integer representation of the board. Defaults to 0.
        :attr turn: an integer representation of which player is moving. Can be
                    be 0 or 1. Defaults to 0.
        :attr player_wins: integer count of how many times the player has won
                    against the computer. Defaults to 0.
        :attr player_losses: integer count of how many times the player has
                    lost to the computer. Defaults to 0.
        :attr ties: integer count of tied games between player and computer.
                    Defaults to 0.
        """
        super(TicTacToeBoard, self).__init__()
        self.board = 0x00000
        self.turn = 0
        self.player_wins = 0
        self.player_losses = 0
        self.ties = 0
        
    def _convert_move(self, square):
        """
        Converts the number of a square into its binary representation.
        
        As explaned in the docs for the class, if an 'X' occupies the square, 
        the square takes the binary value '1 1' [decimal: 3], or for
        an '0' it takes '1 0' [decimal: 2]. If you add 2 to self.turn, you get
        the value for the square.
        
        :param square: integer between 0 and 8
        :return: integer
        """
        try:
            move = int(square)
        except (ValueError, TypeError):
            return None
        
        if not 0 <= move <= 8:
            return None
        return (self.turn + 2) << (2* move)
    
    def _is_valid(self, move):
        """
        Checks if a current move is going to an empty square on the board.
        Returns True if the square is empty, and False if the square is filled
        or if move is None (i.e., self._convert_move decided that move was
        originally invalid input).
        
        :param move: an integer that has been generated using self._convert_move
        :return: boolean
        """
        # TODO: implement
        return False
    
    def _set_turn(self):
        """Alternates the current self.turn between 0 and 1."""
        self.turn = ~self.turn & 0x1
    
    def apply_move(self, square):
        """
        Checks the validity of a given move and applies it to the game board. 
        Returns True if the move was applied; False otherwise.
        
        :param square: integer between 0 and 8
        :return: boolean
        """
        move = self._convert_move(square)
        if self._is_valid(move):
            self.board += move
            return True
        return False
    
    def is_computer_turn(self):
        """
        Determines whether it's the computer's turn to make a move. 
        The human player always goes when self.turn=0, and the computer goes 
        when self.turn=1
        
        :return: boolean
        """
        return bool(self.turn)
    
    