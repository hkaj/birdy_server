#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Birdy
    ~~~~~~~~

    The server part of Birdy.

    :license: GNUL/GPLv3, see LICENSE for more details.
"""

from contextlib import closing
from flask import Flask
import psycopg2

# create and config the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BIRDY_SETTINGS', silent=True)


def connect_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    conn = psycopg2.connect(
        database=database,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port
    )
    return conn


def init_db():
    """Initializes the database."""
    db = connect_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def retrieve_user(username):
    pass


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
    pass


@app.route('/utilisateur/<username>', methods=['GET', 'PUT', 'DELETE'])
def manage_user(username):
    if request.method == 'GET':
        retrieve_user(username)
    elif request.method == 'PUT':
        update_user(username)
    elif request.method == 'DELETE':
        delete_user(username)


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
