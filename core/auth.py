#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import xml.etree.ElementTree as ET

from flask import abort, Flask, escape, request, session
from passlib.hash import sha256_crypt

from core.db import Retriever


def check_auth(session):
    if 'username' in session:
        xml_res = ET.fromstring("<response></response>")
        msg = ET.Element('message')
        # escape will protect against XSS if we decide to render this
        msg.text = "%s - You are authenticated." % escape(session['username'])
        xml_res.append(msg)
        return ET.dump(xml_res)
    return None


def login(request, session):
    xml_res = ET.fromstring("<response></response>")
    login, passwd = request.form['usernm'], request.form['userpwd']
    db_info = json.loads(Retriever(
        ['login_user', 'password'],
        'utilisateur',
        "login_user='%s'" % login
    ).fetch())
    # if the user exists and the password matches
    if 'password' in db_info.keys() and sha256_crypt.verify(passwd, db_info['password']):
        session['username'] = login
        msg = ET.Element('message')
        msg.text = '%s - You are now authenticated.' % escape(login)
        xml_res.append(msg)
        return ET.dump(xml_res)
    else:
        abort(401)


def logout(session):
    session.pop('username', None)
    xml_res = ET.fromstring("<response></response>")
    msg = ET.Element('message')
    msg.text = 'Log out.'
    xml_res.append(msg)
    return ET.dump(xml_res)
