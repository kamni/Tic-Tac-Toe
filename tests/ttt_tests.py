import random
import unittest

from app.ttt import *


O_MOVES = ((0, 0b000000000000000010), (1, 0b000000000000001000), 
           (2, 0b000000000000100000), (3, 0b000000000010000000), 
           (4, 0b000000001000000000), (5, 0b000000100000000000),
           (6, 0b000010000000000000), (7, 0b001000000000000000), 
           (8, 0b100000000000000000))

X_MOVES = ((0, 0b000000000000000011), (1, 0b000000000000001100), 
           (2, 0b000000000000110000), (3, 0b000000000011000000), 
           (4, 0b000000001100000000), (5, 0b000000110000000000),
           (6, 0b000011000000000000), (7, 0b001100000000000000), 
           (8, 0b110000000000000000))

WINNING_MOVES = (0b101010000000000000, 0b100000001000000010,
                 0b100000000000101000, 0b001000000010000010,
                 0b000010101000000000, 0b000010000000100010,
                 0b000000100000001010, 0b000000001010100000)

LAST_MOVES = ((0b100010000000000000, 7), (0b100000001000000000, 0),
              (0b000000000000101000, 8), (0b001000000000000010, 3),
              (0b000010100000000000, 4), (0b000010000000000010, 2),
              (0b000000000000001010, 5), (0b000000001000100000, 3))


class TicTacToeBoardTests(unittest.TestCase):
    # Testing done in binary as a second check to hex calculations in main class
    
    def generate_board(self, empty_squares):
        """
        A helper method to randomly generate a game board.
        
        :param empty_squares: list of squares that should not have an 'X' or 'O'
        """
        board = 0
        for i in range(8, -1, -1):
            match = not (i in empty_squares)
            new_square = (int(match) << 1) + (random.randint(0, 1) 
                                              if match else 0)
            board = (board << 2) + new_square
        return board
    
    def insert_random_moves(self, winning_board, winning_player, pieces=2):
        """
        Helper method to insert random pieces into an existing game board.
        The game board should consist of one of the 'WINNING_MOVES' boards 
        above, and the winning player should be the one that has won the game.
        
        Note: do not include more pieces than there are empty slots on the 
            board.
        
        :param winning_board: an integer from WINNING_MOVES
        :param winning_player: integer representing the player, either 1 or 2
        :param pieces: number of random pieces to insert for the losing. Note 
            that inserting more than 2 pieces may result in a board where the
            losing player actually wins
        :return: integer
        """
        if not pieces:
            return winning_board
        
        # WINNING_MOVES has values for Player 1. We need to update them to
        # Player 2 if that player was specified
        if winning_player == 2:
            for i in range(0, 18, 2):
                mask = 2 << i
                if mask & winning_board:
                    winning_board = winning_board | (1 << i)
            
        losing_player = ~winning_player & 0b11
        return self.insert_random_opponent_moves(winning_board, 
                                                 losing_player, 
                                                 pieces)
        
    def insert_random_opponent_moves(self, board, opponent, moves=2):
        """
        Helper method that inserts moves from an opponent into a board.
        Returns the integer representation of the updated board
        
        :param board: integer representing a board
        :param opponent: integer representing the opponent (1 or 2)
        :param moves: number of moves to insert
        :return: integer
        """
        if not moves:
            return board
        
        # this isn't intended to be a smart algorithm; simply a quick-and-dirty
        # one for testing purposes to get as random as possible
        while moves:
            for i in range(0, 18, 2):
                mask = 2 << i
                if not mask & board:
                    if random.randint(0, 1):
                        board = board | ((opponent + 1) << i)
                        moves -= 1
                        if not moves:
                            return board
    
    def test__init(self):
        # defaults
        ttt = TicTacToeBoard()
        for attr in ('board', 'turn', 'player_wins', 'player_losses', 
                     'ties', 'game_over'):
            self.assertEquals(0, getattr(ttt, attr))
    
    def test__apply_move(self):
        ttt = TicTacToeBoard()
        
        # should error if invalid player is used
        for player in (-1, 0, 3):
            self.assertRaises(AssertionError, ttt._apply_move, 0, 0, player)
        
        # empty board should always apply
        move, ttt.board = ttt._apply_move(3, ttt.board, 1)
        self.assertEquals(3, move)
        self.assertEquals(0b000000000010000000, ttt.board)
        
        # some intermediate test cases
        move, ttt.board = ttt._apply_move(5, ttt.board, 2)
        self.assertEquals(5, move)
        self.assertEquals(0b000000110010000000, ttt.board)
        
        move, ttt.board = ttt._apply_move(5, ttt.board, 1)
        self.assertIsNone(move)
        self.assertEquals(0b000000110010000000, ttt.board)
        move, ttt.board = ttt._apply_move(8, ttt.board, 1)
        self.assertEquals(8, move)
        self.assertEquals(0b100000110010000000, ttt.board)
        
        # full board should never apply
        board = 0b101011101110101111
        for player in (1, 2):
            for square in range(9):
                move, board = ttt._apply_move(square, board, player)
                self.assertIsNone(move)
                self.assertEquals(0b101011101110101111, board, player)
    
    def test__assert_valid_player(self):
        ttt = TicTacToeBoard()
        
        for bad_player in (-1, 0, 3, None):
            self.assertRaises(AssertionError, ttt._assert_valid_player, bad_player)
            
        for good_player in (1, 2):
            self.assertIsNone(ttt._assert_valid_player(good_player))
    
    def test__best_move(self):
        ttt = TicTacToeBoard()
        
        # some standard test cases
        potential_moves = {3: 1}
        self.assertEquals((3, 1), ttt._best_move(potential_moves, 1))
        self.assertEquals((3, 1), ttt._best_move(potential_moves, 2))
        
        potential_moves = {1: 0, 3: 0, 6: -22, 7: -22, 8: 3, 2: 3}
        self.assertTrue(ttt._best_move(potential_moves, 1) in [(6, -22), (7, -22)])
        self.assertTrue(ttt._best_move(potential_moves, 2) in [(2, 3), (8, 3)])
        
        potential_moves = {1: -1, 5: -1, 3: 2, 4: 0, 6: 2, 8: 0}
        self.assertTrue(ttt._best_move(potential_moves, 1) in [(1, -1), (5, -1)])
        self.assertTrue(ttt._best_move(potential_moves, 2) in [(3, 2), (6, 2)])
        
        # problem case
        for player in (1, 2):
            self.assertEquals(None, ttt._best_move({}, player))
    
    def test__board_for_player(self):
        ttt = TicTacToeBoard()
        
        for i, board in enumerate((0b111011101110111011, 0b101110111011101110)):
            for player, playerboards in ((1, (0b001000100010001000,
                                              0b100010001000100010)),
                                         (2, (0b100010001000100010, 
                                              0b001000100010001000))):
                self.assertEquals(playerboards[i], 
                                  ttt._board_for_player(player, board))
    
    def test__calculate_board_costs(self):
        ttt = TicTacToeBoard()
        board = 0b110011101000100011
        
        cost_dict = ttt._calculate_board_costs(board)
        self.assertEquals(6, len(cost_dict))
        for board, player, value_dict in ((0b110011101000100011, 2, {1: -9, 3:0, 7: 10}),
                                          (0b110011101011100011, 1, {1: 9, 7:0}),
                                          (0b111011101011100011, 2, {1: 0}),
                                          (0b110011101011101011, 2, {7: 10}),
                                          (0b110011101000101111, 1, {3: -10, 7: 0}),
                                          (0b111011101000101111, 2, {3: 0})):
            self.assertEquals(value_dict, cost_dict[(board, player)])        
        
    def test__calculate_board_variations(self):
        ttt = TicTacToeBoard()
        
        # simple test: only one move
        board = 0b001011101011101111
        board_list, board_dict, revisit = ttt._calculate_board_variations(board, 2)
        self.assertEquals([], board_list)
        self.assertEquals({8: 0}, board_dict)
        self.assertEquals([], revisit)
        
        # complex test: lots of moves
        board = 0b110000000000000010
        board_list, board_dict, revisit = ttt._calculate_board_variations(board, 2)
        self.assertEquals([(0b110000000000001110, 1),
                           (0b110000000000110010, 1),
                           (0b110000000011000010, 1),
                           (0b110000001100000010, 1),
                           (0b110000110000000010, 1),
                           (0b110011000000000010, 1),
                           (0b111100000000000010, 1)], board_list)
        self.assertEquals(len(board_list), len(board_dict))
        self.assertEquals(len(board_list), len(revisit))
        
        expected_moves = [1, 2, 3, 4, 5, 6, 7]
        for move in expected_moves:
            self.assertTrue(move in board_dict)
            self.assertIsNone(board_dict[move])
        
        for square, next_move in zip(expected_moves, board_list):
            self.assertTrue((board, 2, square, next_move[0]) in revisit)

        # some game-ending moves, some continuing moves
        board = 0b000011101111100010
        board_list, board_dict, revisit = ttt._calculate_board_variations(board, 1)
        self.assertEquals([(0b001011101111100010, 2),
                           (0b100011101111100010, 2)], board_list)
        self.assertEquals(3, len(board_dict))
        self.assertEquals(LOSS_VALUE, board_dict[1])
        self.assertEquals(len(board_list), len(revisit))
        
        expected_moves = [7, 8]
        for move in expected_moves:
            self.assertTrue(move in board_dict)
            self.assertIsNone(board_dict[move])
        
        for square, next_move in zip(expected_moves, board_list):
            self.assertTrue((board, 1, square, next_move[0]) in revisit)

    def test__choose_square(self):
        ttt = TicTacToeBoard()
        
        # should follow moves from PLAYBOOK
        for board, player in PLAYBOOK:
            move = ttt._choose_square(board)
            self.assertTrue(move in PLAYBOOK[(board, 2)])
        
        # should always go for a win if next move
        for board, expected_move in LAST_MOVES:
            winning_board = self.insert_random_moves(board, 2, pieces=0)
            move = ttt._choose_square(winning_board)
            self.assertEquals(expected_move, move)
        
        # should always block immediate future win from opponent.
        for board, expected_move in LAST_MOVES:
            move = ttt._choose_square(board)
            self.assertEquals(expected_move, move)
        
        # and the rest will be tested in `test_forty_two`
    
    def test__convert_move(self):
        ttt = TicTacToeBoard()
        
        # testing for player 1
        for move, expected in O_MOVES:
            self.assertEquals(expected, ttt._convert_move(move, 1))
        
        # testing for player 2
        for move, expected in X_MOVES:
            self.assertEquals(expected, ttt._convert_move(move, 2))
            
        # should return None for integers 0 <= move <= 8
        for move in (-2, -1, 9, 10):
            self.assertIsNone(ttt._convert_move(move, 1))
        
        # should return None for moves that can't be converted to integers
        for move in ('a', None, {}):
            self.assertIsNone(ttt._convert_move(move, 2))
    
    def test__game_over_validation(self):
        ttt = TicTacToeBoard()
        
        # player won (shouldn't happen, but we should detect if it does)
        self.assertEquals((True, 1), ttt._game_over_validation(0b101110111000110010))
        
        # computer won
        self.assertEquals((True, 2), ttt._game_over_validation(0b101011101111110010))
        
        # tie
        self.assertEquals((True, None), ttt._game_over_validation(0b101011101111101110))
        
        # game is still going
        self.assertEquals((False, None), ttt._game_over_validation(0b111011001000000010))
    
    def test__get_valid_moves(self):
        ttt = TicTacToeBoard()
        
        # empty board
        self.assertEquals(list(range(9)), ttt._get_valid_moves(0b000000000000000000))
        
        # full board
        self.assertEquals([], ttt._get_valid_moves(0b101110111011101110))
        
        # various samples
        self.assertEquals([3, 5, 7], ttt._get_valid_moves(0b100010001100111110))
        self.assertEquals([2, 8], ttt._get_valid_moves(0b001011101111001011))
        self.assertEquals([0, 1, 4, 6], ttt._get_valid_moves(0b111000100011110000))
    
    def test__has_won(self):
        ttt = TicTacToeBoard()
        
        # winning circumstances
        for player in (1, 2):
            for board in WINNING_MOVES:
                # winning circumstances
                test_board = self.insert_random_moves(board, player)
                self.assertTrue(ttt._has_won(player, test_board))
                
                # losing circumstances
                test_board = self.insert_random_moves(board, (~player & 0b11))
                self.assertFalse(ttt._has_won(player, test_board))
        
        # some tie boards
        for board in (0b101011101111101110, 0b111011111011101010,
                      0b111110111010111010, 0b101110101110111110):
            for player in (1, 2):
                self.assertFalse(ttt._has_won(player, board))
        
        # incomplete games
        for board in (0b000000000000000000, 0b110010000000111010,
                      0b100000001110110010, 0b000011101100100010):
            for player in (1, 2):
                self.assertFalse(ttt._has_won(player, board))

    def test__is_board_full(self):
        ttt = TicTacToeBoard()
        
        # a few random tests where board is full
        for i in range(9):
            board = self.generate_board([])
            self.assertTrue(ttt._is_board_full(board))
        
        # comprehensive, but not exhaustive non-full tests.
        # we'll run each non-full set of tests twice
        for trial in range(2):
            for empty in range(1, 9):
                open_squares = list(range(empty))
                empty_squares = []
                for sqr in range(empty):
                    square = random.choice(open_squares)
                    empty_squares.append(open_squares.pop(open_squares.index(square)))
                
                board = self.generate_board(empty_squares)
                self.assertFalse(ttt._is_board_full(board))
    
    def test__is_valid_move(self):
        ttt = TicTacToeBoard()
        
        # running an exhaustive test
        for empty_square in range(9):
            board = self.generate_board([empty_square])
            
            for moveset in (O_MOVES, X_MOVES):
                for square, move in moveset:
                    self.assertEquals((square == empty_square), 
                                      ttt._is_valid_move(move, board))
    
    def test__is_win(self):
        # we only need to test for Player 1 because 
        # TicTacToeBoard._board_for_player converts the board to a Player 1
        # perspective
        ttt = TicTacToeBoard()
        
        # we only care that it detects the combo amongst the noise, not
        # whether the board is valid
        for combo in WINNING_MOVES:
            board = self.insert_random_opponent_moves(combo, 1, moves=1)
            for test_combo in WINNING_MOVES:
                self.assertEquals((test_combo == combo), ttt._is_win(board, 
                                                                     test_combo))
    
    def test__set_turn(self):
        ttt = TicTacToeBoard()
        self.assertEquals(0, ttt.turn)
        
        # should alternate between 1 and 0
        for turn in (1, 0, 1, 0, 1, 0, 1, 0):
            ttt._set_turn()
            self.assertEquals(turn, ttt.turn)
            
    def test__set_win(self):
        ttt = TicTacToeBoard()
        self.assertEquals((0, 0, 0), (ttt.player_wins, ttt.player_losses, ttt.ties))
        
        # human player wins (should not happen, but we need to test for it)
        ttt._set_win(1)
        self.assertEquals((1, 0, 0), (ttt.player_wins, ttt.player_losses, ttt.ties))
        
        # computer wins
        ttt._set_win(2)
        self.assertEquals((1, 1, 0), (ttt.player_wins, ttt.player_losses, ttt.ties))
        
        # human and computer tie
        ttt._set_win(None)
        self.assertEquals((1, 1, 1), (ttt.player_wins, ttt.player_losses, ttt.ties))
        
        # and another loss for good measure, to make sure we're not just setting
        # it to 1
        ttt._set_win(2)
        self.assertEquals((1, 2, 1), (ttt.player_wins, ttt.player_losses, ttt.ties))
    
    def test_computer_move(self):
        ttt = TicTacToeBoard()
        ttt.turn = 1
        
        # default case: game is still in progress
        ttt.board = 0b101000001011000011
        
        move, game_over, winner = ttt.computer_move()
        self.assertEquals((False, None), (game_over, winner))
        self.assertTrue(move in [6, 5, 2, 1])
        self.assertEquals(0b101011001011000011, ttt.board)
        self.assertEquals(0, ttt.turn)
        
        # it is not the computer's turn
        self.assertEquals((None, False, None), ttt.computer_move())
        self.assertEquals(0b101011001011000011, ttt.board)
        self.assertEquals(0, ttt.turn)
        
        # the game has ended
        ttt.turn = 1
        move, game_over, winner = ttt.computer_move()
        self.assertEquals((True, 2), (game_over, winner))
        self.assertEquals(2, move)
        self.assertEquals(0b101011001011110011, ttt.board)
        self.assertEquals(0, ttt.turn)
    
    def test_get_square_label(self):
        ttt = TicTacToeBoard()
        ttt.board = 0b111011001011001000
        
        # human
        for square in (7, 4, 1):
            self.assertEquals(PLAYER1, ttt.get_square_label(square))
        
        # computer
        for square in (8, 6, 3):
            self.assertEquals(PLAYER2, ttt.get_square_label(square))
        
        # no one
        for square in (5, 2, 0):
            self.assertEquals("", ttt.get_square_label(square))
    
    def test_human_move(self):
        ttt = TicTacToeBoard()
        
        # default case: game is still in progress
        ttt.board = 0b100000001011000011
        self.assertEquals((7, False, None), ttt.human_move(7))
        self.assertEquals(0b101000001011000011, ttt.board)
        self.assertEquals(1, ttt.turn)
        
        # it is not the human's turn
        self.assertEquals((None, False, None), ttt.human_move(6))
        self.assertEquals(0b101000001011000011, ttt.board)
        self.assertEquals(1, ttt.turn)
        
        # the move isn't valid
        ttt.turn = 0
        self.assertEquals((None, False, None), ttt.human_move(3))
        self.assertEquals(0b101000001011000011, ttt.board)
        self.assertEquals(0, ttt.turn)
        
        # the game has ended
        self.assertEquals((6, True, 1), ttt.human_move(6))
        self.assertEquals(0b101010001011000011, ttt.board)
        self.assertEquals(1, ttt.turn)
        
        # making a move after the game has ended
        ttt.turn = 0
        self.assertEquals((None, True, None), ttt.human_move(1))
        self.assertEquals(0b101010001011000011, ttt.board)
        self.assertEquals(0, ttt.turn)
        
    
    def test_is_computer_turn(self):
        ttt = TicTacToeBoard()
        for turn in (0, 1):
            ttt.turn = turn
            self.assertEquals(bool(turn), ttt.is_computer_turn())
            
    def test_player_stats(self):
        ttt = TicTacToeBoard()
        ttt.player_wins = 1
        ttt.player_losses = 2
        ttt.ties = 4
        
        # player 1 (human)
        self.assertEquals("(Player %s)\n\nWins: 1\nLosses: 2\nTies: 4" % PLAYER1,
                          ttt.player_stats(1))
        
        # player 2 (computer)
        self.assertEquals("(Player %s)\n\nWins: 2\nLosses: 1\nTies: 4" % PLAYER2,
                          ttt.player_stats(2))
    
    def test_reset_board(self):
        ttt = TicTacToeBoard()
        ttt.board = "0b101111100000100000"
        self.assertNotEquals(0, ttt.board)
        
        ttt.reset_board()
        self.assertEquals(0, ttt.board)
        
    def test_forty_two(self):
        # comprehensive testing of the computer selection mechanic
        ttt = TicTacToeBoard()
        
        # since this is probabilistic, let's run this a few times to
        # increase our confidence that the computer won't lose
        for i in range(4):
            # reset PLAYBOOK from previous trials
            PLAYBOOK = {(0x00000, 2): {8: -100, 6: -100, 4: -100, 2: -100},
                        (0x20000, 2): {0: -100},
                        (0x02000, 2): {0: -100},
                        (0x00200, 2): {0: -100},
                        (0x00020, 2): {0: -100},
                        (0x00002, 2): {8: -100, 6: -100, 4: -100, 2: -100},
                        (0x08000, 2): {8: -100, 6: -100},
                        (0x00800, 2): {6: -100, 4: -100},
                        (0x00080, 2): {4: -100, 2: -100},
                        (0x00008, 2): {8: -100, 2: -100}}
            
            game_in_the_known_universe = [0x00000, 0x20000, 0x02000, 0x00200, 
                                          0x00020, 0x00002, 0x08000, 0x00800, 
                                          0x00080, 0x00008] # starting moves
            
            while game_in_the_known_universe:
                current_game = game_in_the_known_universe.pop(0)
                moves = ttt._get_valid_moves(current_game)
                for square in moves:
                    ttt.board = current_game
                    ttt.turn = 0
                    square, game_over, winner = ttt.human_move(square)
                    self.assertNotEquals(1, winner)
                    
                    if not game_over:
                        game_over = ttt.computer_move()[1]
                        if not game_over and ttt.board not in game_in_the_known_universe:
                            game_in_the_known_universe.append(ttt.board)

            
            
