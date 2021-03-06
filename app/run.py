"""
UI classes for running this app. Logic can be found in ttt.py.
"""
import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from ttt import TicTacToeBoard 

HUMAN_NAME = "[color=c60f13]You[/color] "
COMPUTER_NAME = "[color=2ba6cb]Josh[/color] "


class OpeningFrame(BoxLayout):
    """First screen player will see. Layout in tictactoe.kv"""
    pass


class TicTacToeFrame(BoxLayout):
    """Screen where game is played. Layout in tictactoe.kv"""
    board = TicTacToeBoard()
    
    def computer_move(self):
        """
        Computer takes a turn, then returns if game is finished and who won
        
        :return: (boolean, integer)
        """
        square, game_over, winner = self.board.computer_move()
        self.set_square(square)
        return game_over, winner
    
    def player_move(self, square):
        """
        Player takes a turn, then the computer moves if player didn't win
        
        :param square: integer of the square that the player just selected
        """
        self.set_turn_label("")
        
        square, game_over, winner = self.board.human_move(square)
        self.set_square(square)
        
        if not game_over:
            game_over, winner = self.computer_move()

        if game_over:
            self.update_scores()
            self.set_new_game_button(hide=False)
    
    def player_text(self, player_number):
        """
        Text to display scores of players
        
        :param player_number: integer representing the player (1, 2)
        """
        if player_number == 1:
            name_text = HUMAN_NAME
        else:
            name_text = COMPUTER_NAME
        return name_text + self.board.player_stats(player_number)
    
    def reset_game(self, btn):
        """
        Resets the game board (but not the scores) for another game
        
        :param button: argument passed by kivy, but not used by this function
        """
        self.set_new_game_button(hide=True)
        self.board.reset_board()
        self.update_squares()
        
        if self.board.is_computer_turn():
            self.computer_move()
            self.set_turn_label("[color=000000]Now your turn...[/color]")
        else:
            self.set_turn_label("[color=000000]You go first...[/color]")
    
    def set_new_game_button(self, hide):
        """
        Hides or displays the 'Start Another Game' button.
        
        :param hide: boolean indicating whether to hide the button (True) or
                show the button (False)
        """
        ph = self.placeholder
        
        if hide:
            ph.remove_widget(self.new_game_btn)
            ph.add_widget(self.placeholder_label)
            self.new_game_btn = None
        else:
            ph.remove_widget(self.placeholder_label)
            if not getattr(self, 'new_game_btn', None):
                self.new_game_btn = Button(text='[color=000000]Start Another Game[/color]',
                                           background_normal="img/new-game-btn.png",
                                           on_press=self.reset_game,
                                           size_hint=(1, .15))
                ph.add_widget(self.new_game_btn)
    
    def set_square(self, square):
        """
        Sets the text for the indicated square based on the state of the board
        
        :param square: integer representing the square to update (0 to 8)
        """
        if square is not None:
            getattr(self, "square%s" % square).text = self.square_label(square)

    def set_turn_label(self, text):
        """
        Updates a label that displays at the beginning of each game.
        
        :param text: what the label should say. Becomes an empty string during
                game play
        """
        self.go_first_label.text = text
    
    def square_label(self, square):
        """
        Gets the 'X' or 'O' label for the indicated square
        
        :param square: integer representing the square (0 to 8)
        """
        return self.board.get_square_label(square)
    
    def update_scores(self):
        """Updates the text displaying player scores"""
        self.player1_score.text = self.player_text(1)
        self.player2_score.text = self.player_text(2)
        
    def update_squares(self):
        """Updates all squares with the current board state"""
        for square in range(9):
            self.set_square(square)


class ExitFrame(BoxLayout):
    """Last screen of the game, showing a summary of player scores"""
    
    def exit_text(self):
        """
        The text to display to the player, depending on game outcome.
        
        :return: string        
        """
        try:
            board = self.board
            if not (board.player_wins or board.player_losses or board.ties):
                return "Running away so soon?"
            return "A strange game. The only winning move is not to play."
        except AttributeError:
            # the tic-tac-toe screen hasn't passed control over yet
            return ""
    
    def player1_score(self):
        """
        Number of wins for player 1 (the human)
        
        :return: string
        """
        try:
            return "%s\n%s" % (HUMAN_NAME, self.board.player_wins)
        except AttributeError:
            # the tic-tac-toe screen hasn't passed control over yet
            return ""
    
    def player2_score(self):
        """
        Number of wins for player 2 (the computer)
        
        :return: string
        """
        try:
            return "%s\n%s" % (COMPUTER_NAME, self.board.player_losses)
        except AttributeError:
            # the tic-tac-toe screen hasn't passed control over yet
            return ""
    
    def tie_score(self):
        """
        Number of ties for the players
        
        :return: string
        """
        try:
            return "[color=e2c925]Ties[/color]: %s" % self.board.ties
        except AttributeError:
            # yes, we know tic-tac-toe screen still has control of the board
            return ""
    
    def update_text(self):
        """Updates all labels on this screen"""
        self.player1.text = self.player1_score()
        self.player2.text = self.player2_score()
        self.ties.text = self.tie_score()
        self.exit.text = self.exit_text()


class TicTacToeApp(App):
    """Primary class for running the game"""
    
    def build(self):
        # the three screens we'll use for this game
        self.root = BoxLayout()
        self.opening = OpeningFrame()
        self.tic_tac_toe = TicTacToeFrame()
        self.exit_screen = ExitFrame()
        
        self.exit_screen.board = self.tic_tac_toe.board
        self.root.add_widget(self.opening)
        return self.root
    
    def load_game(self):
        """Exchanges the opening screen for the game board"""
        self.root.remove_widget(self.opening)
        self.root.add_widget(self.tic_tac_toe)
        
    def quit_game(self):
        """Replaces the game board with the exit screen"""
        self.exit_screen.update_text()
        self.root.remove_widget(self.tic_tac_toe)
        self.root.add_widget(self.exit_screen)


if __name__ == '__main__':
    TicTacToeApp().run()