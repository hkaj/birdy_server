#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json


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


class Retriever(object):
    """
    Retrieves data from the DB.
    The 'fields' param accepts wildcards.
    They still need to be in a list though
    """
    def __init__(self, fields, table, cond=None):
        super(Retriever, self).__init__()
        self.fields = fields
        self.table = table
        self.condition = cond
        self.db = connect_db()

    def build_req(self):
        req = "SELECT %s FROM %s WHERE %s;" % (', '.join(self.fields), self.table, self.condition)
        req = req.split('WHERE')[0] if not self.condition else req  # Removes the condition part
        return req

    def jsonify(self, result):
        json_result = []
        for line in result:
            dict_res = {self.fields[pos]: self.line[pos] for pos in len(self.fields)}
            json_result.append(json.dumps(dict_res))
        json_result = json_result[0] if len(json_result) == 1 else json_result
        return "%s" % json_result

    def fetch(self):
        cur = self.db.cursor()
        req = self.build_req()
        cur.execute(req)
        res = self.jsonify(cur.fetchall())
        cur.close()
        db.close()
        return res


class Updater(object):
    """Updates DB data."""
    def __init__(self, table, data_dict, cond=None):
        super(Inserter, self).__init__()
        self.table = table
        self.data_dict = data_dict
        self.condition = cond
        self.db = connect_db()

    def build_req(self):
        modified_fields = ', '.join(['%s=%s' % (k, v) for k, v in self.data_dict.iteritems()])
        req = "UPDATE %s SET %s WHERE %s;" % (
            self.table, modified_fields, self.condition)
        req = re.split('WHERE')[0] if not self.condition else req  # Removes the condition part
        return req

    def update(self):
        req = self.build_req()
        cur = self.db.cursor()
        try:
            cur.execute(req)
            db.commit()
            # we could use it to return the modified user.
            # resp = Retriever(['*'], self.table, self.condition).fetch()
            cur.close()
            db.close()
            return '''{"resp": "OK"}'''
        except:
            return '''{"resp": "ERROR - Failed to update the values."}'''


class Deleter(object):
    """Delete lines in the DB."""
    def __init__(self, table, cond):
        super(Deleter, self).__init__()
        self.table = table
        self.condition = cond
        self.db = connect_db()

    def build_req(self):
        req = "DELETE FROM %s WHERE %s" % (self.table, self.condition)
        return req

    def delete(self):
        req = self.build_req()
        cur = self.db.cursor()
        try:
            cur.execute(req)
            db.commit()
            cur.close()
            return '''{"resp": "OK"}'''
        except:
            return '''{"resp": "ERROR - Failed to remove the data from the database."}'''


class Inserter(object):
    """Insert data into the DB."""
    def __init__(self, table, data_dict):
        super(Inserter, self).__init__()
        self.table = table
        self.data_dict = data_dict
        self.db = connect_db()

    def build_req(self):
        req = "INSERT INTO %s(%s) VALUES (%s);" % (
            self.table, ', '.join(self.data_dict.keys()), ', '.join(self.data_dict.values()))
        return req

    def insert(self):
        req = self.build_req()
        cur = self.db.cursor()
        try:
            cur.execute(req)
            db.commit()
            cur.close()
            return '''{"resp": "OK"}'''
        except:
            return '''{"resp": "ERROR - Failed to save the new data."}'''