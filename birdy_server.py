#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Birdy
    --------

    The server part of Birdy.

    :license: GNUL/GPLv3, see LICENSE for more details.
"""

from contextlib import closing
from flask import Flask
import json
import psycopg2
from db_utils import Retriever, Deleter, Inserter

# create and config the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BIRDY_SETTINGS', silent=True)


def init_db():
    """Initializes the database."""
    db = db_utils.connect_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def update_user(username):
    pass


def delete_user(username):
    pass


def get_auth():
    pass


def make_auth():
    pass


def remove_auth():
    pass


def retrieve_position(login):
    pass


def update_position(login):
    pass


def create_relative(login1, login2):
    pass


def update_relative(login1, login2):
    pass


def delete_relative(login1, login2):
    pass


@app.route('/utilisateurs')
def get_all_users():
    pass


@app.route('/utilisateur', methods=['POST', ])
def create_user():
    user = Retriever('login_user', 'utilisateur', 'login_user=%s' % request.form['login']).fetch()
    if user != '[]':
        return '''{"resp": "ERROR - User already exists."}'''
    else:
        return Inserter('utilisateur', request.form).insert()


@app.route('/utilisateur/<username>', methods=['GET', 'PUT', 'DELETE'])
def manage_user(username):
    fields = ['login_user', 'numero_tel', 'e_mail', 'nom', 'prenom', 'numero_tel_sec']
    table = 'utilisateur'
    if request.method == 'GET':
        condition = "login_user=%s" % username
        return Retriever(fields, table, condition).fetch()
    elif request.method == 'PUT':
        user = Retriever('login_user', 'utilisateur', 'login_user=%s' % username).fetch()
        if user == '[]':
            return '''{"resp": "ERROR - User not found."}'''
        else:
            return Updater('utilisateur', request.form, 'login_user=%s' % username).update()
    elif request.method == 'DELETE':
        return Deleter('utilisateur', 'login_user=%s' % username)


@app.route('/authorization', methods=['GET', 'POST', 'DELETE'])
def manage_auth():
    # the functions will need data from the request
    if request.method == 'GET':
        get_auth()
    elif request.method == 'POST':
        make_auth()
    elif request.method == 'DELETE':
        remove_auth()


@app.route('/position/<login>', methods=['GET', 'PUT', ])
def manage_user(login):
    # the functions will need data from the request
    if request.method == 'GET':
        retrieve_position(login)
    elif request.method == 'PUT':
        update_position(login)


@app.route('/relatives/<login>')
def get_all_relatives(login):
    pass


@app.route('/relative/<login1>/<login2>', methods=['POST', 'PUT', 'DELETE'])
def manage_relative(login1, login2):
    if request.method == 'POST':
        create_relative(login1, login2)
    elif request.method == 'PUT':
        update_relative(login1, login2)
    elif request.method == 'DELETE':
        delete_relative(login1, login2)


@app.route('/relativesPositions/<login>')
def get_relative_positions(login):
    pass
