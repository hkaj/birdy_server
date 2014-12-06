#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import psycopg2

from urlparse import urljoin


def connect_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    birdy_dir = os.getenv('BIRDY', None)
    if birdy_dir:
        settings_file = urljoin(birdy_dir, 'birdy.cfg')
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
        birdy_dir = os.getenv('BIRDY', None)
        if birdy_dir:
            path = urljoin(birdy_dir, 'sql/')
            with open(urljoin(path, filename), mode='r') as f:
                db.cursor().execute(f.read())
            db.commit()
            db.close()


parser = argparse.ArgumentParser()
parser.add_argument('--action', help='init, clear, or drop.')
args = parser.parse_args()
args = vars(args)
if args['action'] == 'init':
    execute('schema.sql')
elif args['action'] == 'clear':
    execute('clear_db.sql')
elif args['action'] == 'drop':
    execute('drop_db.sql')
else:
    print("'db_utils -h' for help.")
