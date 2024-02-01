from __future__ import annotations
from manage import db
from flask_login import UserMixin
from os import system
from gen_utilities import try_commit, log
import csv
import json

#ASSOCIATION TABLES
user_game_at = db.Table(
    "user_game_at",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("game_id", db.String(25), db.ForeignKey("game.id"))
)

user_friend_at = db.Table(
    "user_friend_at",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("friend_id", db.Integer, db.ForeignKey("friend.id"))
)

#MODELS
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    date_joined = db.Column(db.DateTime())
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    current_games = db.relationship('Game', secondary=user_game_at, backref="players")
    friend_ref = db.relationship('Friend', uselist=False, backref="user")
    friends = db.relationship('Friend', secondary=user_friend_at, backref="friended_users")

    def __repr__(self):
        return self.username
    
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))

class Game(db.Model):
    id = db.Column(db.String(25), primary_key=True)
    turn = db.Column(db.Integer)
    king = db.Column(db.Integer)
    victor = db.Column(db.Integer)
    finished = db.Column(db.DateTime())
    last_move = db.Column(db.String(200))

    def init_board(self):
        with open(f'games/{self.id}.csv', 'w') as new_brd:
            with open('starter.csv') as strt_brd:
                start_rdr = csv.reader(strt_brd)
                new_board_wrtr = csv.writer(new_brd)
                new_board_wrtr.writerows(start_rdr)

    def retrieve_board(self):
        try:
            with open(f'games/{self.id}.csv') as brd:
                return list(csv.reader(brd))
        except Exception:
            self.init_board()
            return self.retrieve_board()

    def retrieve_old_board(self):
        if self.last_move:
            move = json.loads(self.last_move)
            frm = move['start']
            to = move['end']
            board = self.retrieve_board()
            board[frm[0]][frm[1]] = move['type']
            board[to[0]][to[1]] = '0'
            for pair in move['caps']:
                idcs = pair[1]
                board[idcs[0]][idcs[1]] = pair[0]
            return board
        else:
            return self.retrieve_board()

    def update_board(self, move):
        brd = self.retrieve_board()
        frm = move['start']
        to = move['end']
        brd[frm[0]][frm[1]] = '0'
        brd[to[0]][to[1]] = move['type']
        for cap in move['caps']:
            cap_idcs = cap[1]
            brd[cap_idcs[0]][cap_idcs[1]] = '0'
        with open(f'games/{self.id}.csv', 'w') as old_brd:
            wrtr = csv.writer(old_brd)
            wrtr.writerows(brd)

    def delete(self):
        system(f'rm games/{self.id}.csv')
        db.session.delete(self)
        try_commit(disp=log)