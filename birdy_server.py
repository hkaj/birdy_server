#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Birdy
    --------

    The server part of Birdy.

    :license: GNUL/GPLv3, see LICENSE for more details.
"""

from contextlib import closing
from db_utils import Retriever, Deleter, Inserter
from flask import Flask, escape, request
import json
from passlib import sha256_crypt
import psycopg2
import xml.etree.ElementTree as ET

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


def check_auth(session):
    xml_res = ET.fromstring("<response></response>")
    msg = ET.Element('message')
    if 'username' in session:
        # escape will protect against XSS if we decide to render this
        msg.text = "%s - You are authenticated." % escape(session['username'])
    else:
        msg.text = "NULL - You are not authenticated."
    xml_res.append(msg)
    return ET.dumps(xml_res)


def login(request):
    xml_res = ET.fromstring("<response></response>")
    login, passwd = request.form['usernm'], request.form['userpwd']
    db_info = json.loads(Retriever(
        ['login_user', 'password'],
        'utilisateur',
        'login_user=%s' % login
    ).fetch())
    # if the user exists and the password matches
    if 'password' in db_info.keys() and sha256_crypt.verify(passwd, db_info['password']):
        session['username'] = login
        msg = ET.Element('message')
        msg.text = '%s - You are now authenticated.' % escape(login)
        xml_res.append(msg)
        return xml_res
    else:
        abort(401)


def logout(session):
    session.pop('username', None)
    xml_res = ET.fromstring("<response></response>")
    msg = ET.Element('message')
    msg.text = 'Log out.'
    xml_res.append(msg)
    return xml_res


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
        check_auth(request.session)
    elif request.method == 'POST':
        login(request)
    elif request.method == 'DELETE':
        logout()


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


@app.errorhandler(401)
def wrong_credentials():
    xml_res = ET.fromstring("<response></response>")
    msg = ET.Element('message')
    msg.text = 'NULL - Wrong credentials.'
    xml_res.append(msg)
    return xml_res