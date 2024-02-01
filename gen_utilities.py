from manage import db
from flask import flash
from os import system

def try_commit(disp=flash):
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        disp(f'Commit Failure: {e}')

def log(str):
    with open('log.txt', 'a') as fl:
        fl.write(str)

def cache(str):
    with open('cache.txt', 'w') as fl:
        fl.write(str)

def read_cache():
    try:
        with open('cache.txt') as fl:
            contents = fl.readline()
        system('rm cache.txt')
        return contents
    except FileNotFoundError as e:
        return None