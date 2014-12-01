#! /usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

from flask import Flask, escape, request


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
