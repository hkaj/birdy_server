#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Birdy
    --------

    The server part of Birdy.

    :license: GNUL/GPLv3, see LICENSE for more details.
"""

import json
import psycopg2
import xml.etree.ElementTree as ET

from contextlib import closing
from core.auth import check_auth, login, logout
from core.db import Retriever, Deleter, Inserter
from flask import Flask, escape, request, g
from passlib.hash import md5_crypt, sha256_crypt


# create and config the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BIRDY_SETTINGS', silent=True)
app.config['DEBUG'] = True
SECRET_KEY = 'dev.key'


def connect_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    conn = psycopg2.connect(
        database=app.config['DATABASE'],
        user=app.config['USER'],
        password=md5_crypt(app.config['PASSWORD']),
    )
    return conn


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def init_db():
    """Initializes the database."""
    with closing(connect_db()) as db:
        with app.open_resource('sql/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def create_relative(login1, login2):
    condition = 'login_user=%s OR %s' % (login1, login2)
    users = json.loads(Retriever('login_user', 'utilisateur', condition).fetch())
    # Both users exist
    if len(users) == 2:
        rel = Retriever(
            'status',
            'liensUtilisateurs',
            'status=true AND login_user_1=%s AND login_user_2=%s' % (login1, login2)
        ).fetch()
        if rel == '[]':
            data = {}
            data['login_user_1'] = login1
            data['login_user_2'] = login2
            data['type'] = 'proche'
            data['status'] = 'true'
            return Inserter('liensUtilisateurs', data).insert()
        else:
            return '''{"resp": "ERROR - The relation already exists."}'''
    # The second user doesn't exist
    elif len(users) == 1 and users[0]['login_user'] == login1:
        return '''{"resp": "Une invitation va être envoyée à %s pour lui proposer d'utiliser le service."}''' % login2
    # Both users missing
    else:
        return '''{"resp": "ERROR - Users not found."}'''


@app.route('/utilisateurs')
def get_all_users():
    pass


@app.route('/utilisateur', methods=['POST', ])
def create_user():
    user = Retriever('login_user', 'utilisateur', 'login_user=%s' % request.form['login']).fetch()
    if user != '[]':
        return '''{"resp": "ERROR - User already exists."}'''
    else:
        # This way we only store salted hashs, no password.
        request.form['password'] = sha256_crypt.encrypt(request.form['password'])
        res = Inserter('utilisateur', request.form).insert()
        # Init a line in the position table for the new user
        Inserter('position', {'login_user': request.form['login']}).insert()
        return res


@app.route('/utilisateur/<username>', methods=['GET', 'PUT', 'DELETE'])
def manage_user(username):
    fields = ['login_user', 'numero_tel', 'e_mail', 'nom', 'prenom', 'numero_tel_sec']
    table = 'utilisateur'
    if request.method == 'GET':
        condition = "login_user=%s" % username
        return '{"resp": %s}' % Retriever(fields, table, condition).fetch()
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
        check_auth(request.session)
    elif request.method == 'POST':
        login(request)
    elif request.method == 'DELETE':
        logout(request.session)


@app.route('/position/<login>', methods=['GET', 'PUT', ])
def manage_position(login):
    fields = ['id_position', 'login_user', 'latitude', 'longitude', 'vit', 'acc', 'last_update']
    table = 'position'
    condition = 'login_user=%s' % login
    if request.method == 'GET':
        resp = Retriever(fields, table, condition).fetch()
        if resp == '[]':
            return '''{"resp": "ERROR - Failed to read the position."}'''
    elif request.method == 'PUT':
        # check that the user exists
        user = Retriever('login_user', table, 'login_user=%s' % login).fetch()
        if user == '[]':
            return '''{"resp": "ERROR - Failed to update the position."}'''
        else:
            return Updater('position', request.form, condition).update()


@app.route('/relatives/<login>')
def get_all_relatives(login):
    fields = ['login_user_2']
    table = 'liensUtilisateurs'
    condition = 'login_user_1=login_user_2'
    return '{"resp": %s}' % Retriever(fields, table, condition).fetch()


@app.route('/relative/<login1>/<login2>', methods=['POST', 'PUT', 'DELETE'])
def manage_relative(login1, login2):
    if request.method == 'POST':
        create_relative(login1, login2)
    elif request.method == 'PUT':
        # this case isn't useful for now.
        condition = "((login_user_1=%s AND login_user_2=%s) OR (login_user_1=%s AND login_user_2=%s))" % (
            login1, login2, login2, login1)
        return Updater('liensUtilisateurs', {'status': 'true'}, condition).update()
    elif request.method == 'DELETE':
        condition = "((login_user_1=%s AND login_user_2=%s) OR (login_user_1=%s AND login_user_2=%s))" % (
            login1, login2, login2, login1)
        return Deleter('liensUtilisateurs', condition).delete()


@app.route('/relativesPositions/<login>')
def get_relative_positions(login):
    fields = 'rel.login_user_2, pos.latitude, pos.longitude, pos.vit, pos.acc'
    table = 'liensUtilisateurs AS rel LEFT JOIN position AS pos'
    condition = 'rel.login_user_1 = %s AND rel.status = true AND type = proche' % login
    res = Retriever(fields, table, condition).fetch()
    if res == '[]':
        return '''{"resp": "ERROR - Failed to retrieve friends positions."}'''
    return '{"resp": %s}' % res


@app.errorhandler(401)
def wrong_credentials():
    xml_res = ET.fromstring("<response></response>")
    msg = ET.Element('message')
    msg.text = 'NULL - Wrong credentials.'
    xml_res.append(msg)
    return xml_res

if __name__ == "__main__":
    app.run()