#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import psycopg2


def connect_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    settings_file = os.getenv('BIRDY_SETTINGS', None)
    if settings_file:
        with open(settings_file, 'r') as f:
            settings = f.read()
    else:
        print("No config file found. Did you set the env variable?")
        return
    settings = settings.split('\n')[:-1]
    settings = {x[0]: x[1].strip("'") for x in [line.split(' = ') for line in settings]}
    conn = psycopg2.connect(
        database=settings['DATABASE'],
        user=settings['USER'],
        password=settings['PASSWORD'],
    )
    return conn


def execute(filename):
    """Initializes the database."""
    db = connect_db()
    if db:
        with open('sql/%s' % filename, mode='r') as f:
            db.cursor().execute(f.read())
        db.commit()
        db.close()


parser = argparse.ArgumentParser()
parser.add_argument('--action', help='init, clear, or drop.')
parser.add_argument('-h', help='usage: db_utils.py --action=init|clear|drop')
args = parser.parse_args()
if args['action'] == 'init':
    execute('init_db.sql')
elif args['action'] == 'clear':
    clear_db('clear_db.sql')
elif args['action'] == 'drop':
    drop_db('drop_db.sql')
