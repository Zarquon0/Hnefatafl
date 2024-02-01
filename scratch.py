from manage import app
from models import Game, User
from game_utilities import valid_choice, valid_movement, valid_captures, validate_move

with app.app_context():
    game = Game.query.get('hkRbnnlBSbTMbRkyUGksZhslY')
    brd = game.retrieve_board()
    move = {'type': '3', 'start': (0, 5), 'end': (0,2), 'caps': [('1', (0,1))]}
    print(valid_captures(move, brd))