from manage import app, db
from models import User, Friend

to_add = [User(username="Bob Diddly"), User(username="me"), User(username="123"), User(username="qwerty")]
friends =  [Friend(), Friend(), Friend(), Friend()]
for i in range(len(to_add)):
    to_add[i].friend_ref = friends[i]

with app.app_context():
    db.session.add_all(to_add + friends)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()