from manage import app, lm, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, login_user
from models import User, Friend, Game
from forms import LoginForm, RegisterForm, GameForm, FriendForm
from game_utilities import prep_board, detect_victory, validate_move
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import json
from copy import deepcopy
from gen_utilities import try_commit, cache, read_cache

#Configure login manager
@lm.user_loader
def load_user(uid):
    return User.query.get(int(uid))

@lm.unauthorized_handler
def to_login():
    return redirect(url_for('login'))

#CONSTANTS
CHARS = [chr(num) for num in (list(range(65,91)) + list(range(97,123)))]

#HELPERS
def gen_gid():
    return ''.join([random.choice(CHARS) for i in range(25)])

def json_prep(obj, first=True):
    if first:
        obj = deepcopy(obj)
    if type(obj) == list:
        for i in range(len(obj)):
            obj[i] = json_prep(obj[i], first=False)
    elif type(obj) == dict:
        for key in obj.keys():
            obj[key] = json_prep(obj[key], first=False)
    elif hasattr(obj, '__dict__'):
        obj = obj.__dict__
        return json_prep(obj, first=False)
    elif not_jsonable(obj):
        obj = ''
    elif json_encoded(obj):
        return json_prep(json.loads(obj), first=False)
    return obj

def not_jsonable(obj):
    try:
        json.dumps(obj)
        return False
    except (TypeError, OverflowError):
        return True

def json_encoded(obj):
    try: 
        loaded = json.loads(obj)
        return type(loaded) in [list, dict]
    except (TypeError, json.decoder.JSONDecodeError):
        return False
    
def tuplify_move(move):
    move['start'] = tuple(move['start'])
    move['end'] = tuple(move['end'])
    move['caps'] = list(map(lambda pair: (pair[0], tuple(pair[1])), move['caps']))

#Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    elif login_form.validate_on_submit():
        user = User.query.filter(User.username==login_form.username.data).first()
        if not user:
            flash('No user with input username')
            return render_template('login.html', lform=login_form)
        elif user.password_hash and not check_password_hash(user.password_hash, login_form.password.data):
            flash('Incorrect password')
            return render_template('login.html', lform=login_form)
        else:
            login_user(user)
            return redirect(url_for('home'))
    else:
        return render_template('login.html', lform=login_form)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        register_form = RegisterForm()
        if register_form.validate_on_submit():
            usernames = map(lambda user: user.username, User.query.all())
            if register_form.username.data in usernames:
                flash(f'{register_form.username.data} has already been taken. If you created the account with this username, proceed to login. Otherwise, come up with another 😢.')
                return render_template('register.html', rform=register_form)
            phash = register_form.password.data
            if phash:
                phash = generate_password_hash(phash)
            new_user = User(username=register_form.username.data,
                            password_hash=phash,
                            date_joined=datetime.utcnow())
            reference_friend = Friend()
            new_user.friend_ref = reference_friend
            db.session.add_all([new_user, reference_friend])
            try_commit()
            return redirect(url_for('login'))
        return render_template('register.html', rform=register_form)

@app.route('/home', methods=['GET','POST'])
@login_required
def home():
    friend_form = FriendForm()
    if friend_form.validate_on_submit():
        other_player = User.query.filter(User.username==friend_form.friend_username.data).first()
        if not other_player or other_player == current_user:
            flash('No other player of input username found')
        else:
            new_friend = other_player.friend_ref
            current_user.friends.append(new_friend)
            other_player.friends.append(current_user.friend_ref)
            try_commit()
    return render_template('home.html', user=current_user, fform=friend_form)

@app.route('/new_game')
@login_required
def new_game():
    rand = 'user1' in request.args and 'rand' in request.args
    users = 'user1' in request.args and 'user2' in request.args
    if rand or users:
        game = Game(id=gen_gid(), turn=0)
        user1_id = request.args.get('user1')
        user1 = User.query.get(user1_id)
        if rand:
            max_id = len(User.query.all())
            ptntl_ids = list(range(1, max_id + 1))
            ptntl_ids.remove(int(user1_id))
            while True:
                if ptntl_ids:
                        user2_id = random.choice(ptntl_ids)
                        user2 = User.query.get(str(user2_id))
                        games_with_both = list(filter(lambda game: user1 in game.players and user2 in game.players, Game.query.all()))
                        if len(games_with_both) < 3:
                            break
                        ptntl_ids.remove(user2_id)
                else:
                    flash('No users without three other games with you found...')
                    return redirect(url_for('home'))
        elif users:
            user2 = User.query.get(request.args.get('user2'))
            games_with_both = list(filter(lambda game: user1 in game.players and user2 in game.players, Game.query.all()))
            if len(games_with_both) >= 3:
                flash('You may only have up to three games with the same user')
                return redirect(url_for('home'))
        user1.current_games.append(game)
        user2.current_games.append(game)
        try_commit()
        return redirect(url_for('home'))
    else:
        flash('Malformed Request')
        return redirect(url_for('home'))

@app.route('/game/<gid>')
@login_required
def game(gid):
    curr_game = Game.query.get(gid)
    if curr_game:
        selection = request.args.get('selection')
        if selection:
            if current_user == curr_game.players[curr_game.turn] and not curr_game.king:
                if selection == 'invaders':
                    curr_game.king = 1
                    curr_game.turn = 0
                elif selection == 'defenders':
                    curr_game.king = 0
                    curr_game.turn = 1
                try_commit()
            else:
                flash('Naughty, naughty, naughty.')
            return redirect(url_for('game', gid=curr_game.id))
        if curr_game.players[curr_game.turn] == current_user:
            board_rep = curr_game.retrieve_old_board()
        else:
            board_rep = curr_game.retrieve_board()
        prepped_board = prep_board(board_rep)
        return render_template('game.html', 
                            board=prepped_board,
                            game=curr_game,
                            user=current_user,
                            game_data={'board_rep' : board_rep,
                                        'user' : json_prep(current_user),
                                        'game' : json_prep(curr_game),
                                        'players' : json_prep(list(curr_game.players))})
    else:
        return redirect(url_for('home'))

@app.route('/move', methods=['POST'])
@login_required
def move():
    game_data = request.get_json()
    move = game_data['move']
    curr_game = Game.query.get(game_data['gid'])
    tuplify_move(move)
    if validate_move(move, curr_game, current_user):
        curr_game.last_move = json.dumps(move)
        curr_game.update_board(move)
        new_brd = curr_game.retrieve_board()
        if detect_victory(move, new_brd):
            curr_game.victor = curr_game.turn
            curr_game.finished = datetime.utcnow()
            curr_game.players[curr_game.turn].games_won += 1
            for player in curr_game.players:
                player.games_played += 1
        curr_game.turn = 1 if curr_game.turn == 0 else 0
        try_commit(disp=cache)
        fail = read_cache()
        if fail:
            return json.dumps('Herm, there appears to be an error...\n' + fail)
        return json.dumps('success')
    else:
        msg = 'Naughty, naughty, naughty.'
        return json.dumps(msg)

#????
@app.route('/favicon.ico')
def favicon():
    return redirect('/static/media/logo_black.png')