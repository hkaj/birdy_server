#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Birdy
    --------

    The server part of Birdy.

    :license: GNU/GPLv3, see LICENSE for more details.
"""
import simplejson as json
import psycopg2
import xml.etree.ElementTree as ET

from contextlib import closing
from core.auth import check_auth, login, logout
from core.db import Retriever, Deleter, Inserter, Updater
from flask import abort, escape, Flask, g, render_template, request, session, Response
from functools import wraps
from passlib.hash import md5_crypt, sha256_crypt


# create and config the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BIRDY_SETTINGS', silent=True)
app.config['DEBUG'] = False


# make the session permanent (i.e. 31 days)
@app.before_request
def make_session_permanent():
    session.permanent = True


def connect_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    conn = psycopg2.connect(
        database=app.config['DATABASE'],
        user=app.config['USER'],
        password=app.config['PASSWORD'],
    )
    return conn


def auth_required(who=None):
    def auth_decorator(func):
        @wraps(func)
        def auth_checker(*args, **kwargs):
            if not session.get('username'):
                abort(401)
            elif who == 'user':
                # check if the action is intended to be on the logged in user.
                if session.get('username') in request.url:
                    return func(*args, **kwargs)
                else:
                    abort(401)
            elif who == 'user and friends':
                # builds a list of the user and his friends
                condition = "login_user_1='%s'" % session.get('username')
                relatives = json.loads(
                    Retriever(['login_user_2'], 'liensUtilisateurs', condition).fetch())
                if isinstance(relatives, dict):
                    relatives = relatives.values()
                else:
                    relatives = [rel.values()[0] for rel in relatives]
                relatives.append(session.get('username'))
                # check if the action is intended to be on the logged in user or a friend of his.
                if any(rel in request.url for rel in relatives):
                    return func(*args, **kwargs)
                else:
                    abort(401)
            elif who == 'all':
                # All users are allowed to access the ressource
                if session.get('username'):
                    return func(*args, **kwargs)
                else:
                    abort(401)
            else:
                return func(*args, **kwargs)
        return auth_checker
    return auth_decorator


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def create_relative(login1, login2):
    condition = "login_user='%s' OR login_user='%s'" % (login1, login2)
    users = json.loads(Retriever(['login_user'], 'utilisateur', condition).fetch())
    # Both users exist
    if len(users) == 2:
        rel = Retriever(
            ['status'],
            'liensUtilisateurs',
            "status=true AND login_user_1='%s' AND login_user_2='%s'" % (login1, login2)
        ).fetch()
        if rel == '[]':
            data = {}
            data['login_user_1'] = login1
            data['login_user_2'] = login2
            data['type'] = 'proche'
            data['status'] = 'true'
            Inserter('liensUtilisateurs', data).insert()
            data['login_user_1'], data['login_user_2'] = data['login_user_2'], data['login_user_1']
            Inserter('liensUtilisateurs', data).insert()
            return '''{"resp": "OK"}'''
        else:
            return '''{"resp": "ERROR - The relation already exists."}'''
    # The second user doesn't exist
    elif len(users) == 1 and users['login_user'] == login1:
        return u'{"resp": "Une invitation va être envoyée à %s pour lui proposer d\'utiliser le service."}' % login2
    # Both users or first user missing
    else:
        return '''{"resp": "ERROR - Users not found."}'''


@app.route('/utilisateurs')
@auth_required(who='all')
def get_all_users():
    return Retriever(['login_user', 'nom', 'prenom', 'avatar'], 'utilisateur').fetch()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/utilisateur/', methods=['POST', ])
def create_user():
    user = Retriever(['login_user'], 'utilisateur', "login_user='%s'" % request.form.get('login')).fetch()
    if user != '[]':
        return '''{"resp": "ERROR - User already exists."}'''
    else:
        params = {k: v for k, v in request.form.items()}
        # This way we only store salted hashs, no password.
        params['password'] = sha256_crypt.encrypt(params['password'])
        res = Inserter('utilisateur', params).insert()
        # Init a line in the position table for the new user
        Inserter('position', {'login_user': params['login_user']}).insert()
        return res


@app.route('/utilisateur/<username>')
@auth_required(who='user and friends')
def get_user(username):
    fields = ['login_user', 'numero_tel', 'e_mail', 'nom', 'prenom', 'numero_tel_sec', 'statut', 'avatar']
    table = 'utilisateur'
    condition = "login_user='%s'" % username
    return '{"resp": %s}' % Retriever(fields, table, condition).fetch()


@app.route('/utilisateur/<username>', methods=['PUT', 'DELETE', ])
@auth_required(who='user')
def manage_user(username):
    if request.method == 'PUT':
        user = Retriever(['login_user'], 'utilisateur', "login_user='%s'" % username).fetch()
        if user == '[]':
            return '''{"resp": "ERROR - User not found."}'''
        else:
            params = {k: v for k, v in request.form.items()}
            if 'password' in params.keys():
                params['password'] = sha256_crypt.encrypt(params['password'])
            # if the user login is modified, it's also modified in liensUtilisateurs
            if 'login_user' in params.keys():
                # First, let's check if the new username is already taken
                user = Retriever(
                    ['login_user'], 'utilisateur', "login_user='%s'" % params['login_user']).fetch()
                if user != '[]':
                    return '''{"resp": "ERROR - Username already taken."}'''
                else:
                    # Replace username in liensutilisateurs and position tables
                    Updater(
                        'liensutilisateurs',
                        {'login_user_2': params['login_user']},
                        "login_user_2='%s'" % username
                    ).update()
                    Updater(
                        'liensutilisateurs',
                        {'login_user_1': params['login_user']},
                        "login_user_1='%s'" % username
                    ).update()
                    Updater(
                        'position',
                        {'login_user': params['login_user']},
                        "login_user='%s'" % username
                    ).update()
            return Updater('utilisateur', params, "login_user='%s'" % username).update()
    elif request.method == 'DELETE':
        Deleter('position', "login_user='%s'" % username).delete()
        return Deleter('utilisateur', "login_user='%s'" % username).delete()


@app.route('/authorization', methods=['GET', 'POST', 'DELETE'])
def manage_auth():
    # the functions will need data from the request
    if request.method == 'GET':
        auth = check_auth(session)
        if auth:
            return auth
        else:
            xml_res = ET.fromstring("<response></response>")
            msg = ET.Element('message')
            msg.text = 'NULL - You are not authenticated.'
            xml_res.append(msg)
            return ET.tostring(xml_res)
    elif request.method == 'POST':
        return login(request, session)
    elif request.method == 'DELETE':
        return logout(session)


@app.route('/position/<login>', methods=['PUT', ])
@auth_required(who='user')
def update_position(login):
    fields = ['id_position', 'login_user', 'latitude', 'longitude', 'vit', 'acc', 'last_update']
    table = 'position'
    condition = "login_user='%s'" % login
    # check that the user exists
    user = Retriever(['login_user'], table, "login_user='%s'" % login).fetch()
    if user == '[]':
        return '''{"resp": "ERROR - Failed to update the position."}'''
    else:
        return Updater('position', request.form, condition).update()


@app.route('/position/<login>')
@auth_required(who='user and friends')
def get_position(login):
    fields = ['id_position', 'login_user', 'latitude', 'longitude', 'vit', 'acc', 'last_update']
    table = 'position'
    condition = "login_user='%s'" % login
    resp = Retriever(fields, table, condition).fetch()
    if resp == '[]':
        return '''{"resp": "ERROR - Failed to read the position."}'''
    else:
        return '{"resp": %s}' % resp


@app.route('/relatives/<login>')
@auth_required(who='user and friends')
def get_all_relatives(login):
    fields = ['login_user_2']
    table = 'liensUtilisateurs'
    condition = "login_user_1='%s'" % login
    relative_logins = json.loads(Retriever(fields, table, condition).fetch())
    relatives = []
    rel_fields = ['login_user', 'numero_tel', 'e_mail', 'nom', 'prenom', 'numero_tel_sec']
    # Only one relative
    if isinstance(relative_logins, dict):
        rel_condition = "login_user='%s'" % relative_logins['login_user_2']
        relatives.append(json.loads(Retriever(rel_fields, 'utilisateur', rel_condition).fetch()))
    # Several relatives
    elif isinstance(relative_logins, list):
        for relative in relative_logins:
            rel_condition = "login_user='%s'" % relative['login_user_2']
            relatives.append(json.loads(Retriever(rel_fields, 'utilisateur', rel_condition).fetch()))
    return '{"resp": %s}' % json.dumps(relatives)


@app.route('/relative/<login1>/<login2>', methods=['POST', 'PUT', 'DELETE'])
@auth_required(who='user')
def manage_relative(login1, login2):
    if request.method == 'POST':
        return create_relative(login1, login2)
    elif request.method == 'PUT':
        # this case isn't useful for now.
        condition = "((login_user_1='%s' AND login_user_2='%s') OR (login_user_1='%s' AND login_user_2='%s'))" % (
            login1, login2, login2, login1)
        return Updater('liensUtilisateurs', {'status': 'true'}, condition).update()
    elif request.method == 'DELETE':
        condition = "((login_user_1='%s' AND login_user_2='%s') OR (login_user_1='%s' AND login_user_2='%s'))" % (
            login1, login2, login2, login1)
        return Deleter('liensUtilisateurs', condition).delete()


@app.route('/relativesPositions/<login>')
@auth_required(who='user')
def get_relative_positions(login):
    fields = ['rel.login_user_2', 'pos.latitude', 'pos.longitude', 'pos.vit', 'pos.acc']
    table = 'liensUtilisateurs AS rel LEFT JOIN position AS pos ON rel.login_user_2 = pos.login_user'
    condition = "rel.login_user_1='%s' AND rel.status=true AND type='proche'" % login
    res = Retriever(fields, table, condition).fetch()
    if res == '[]':
        return '''{"resp": "ERROR - Failed to retrieve friends positions."}'''
    return '{"resp": %s}' % res


@app.errorhandler(401)
def wrong_credentials(error):
    xml_res = ET.fromstring("<response></response>")
    msg = ET.Element('message')
    msg.text = "401 - Unauthorized"
    xml_res.append(msg)
    return Response(ET.tostring(xml_res), 401)

if __name__ == "__main__":
    app.run()
