from manage import app
from models import Game
from datetime import datetime
from gen_utilities import log
with app.app_context():
	games = Game.query.all()
	now = datetime.utcnow()
	for game in games:
		if game.finished and (now - game.finished).days >= 3:
			log(f'Game {game.id} deleted - {now}')
			game.delete()
	log(f'Cleansing Complete - {now}')