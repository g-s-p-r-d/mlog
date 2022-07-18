import os

import sqlite3
import pandas as pd


# TODO: right way to do it?
def connect(*args, **kwargs):
    return Project(*args, **kwargs)


class Project:

    def __init__(self, project=None):

        self.project = project if project is not None else 'default'

        con = sqlite3.connect(f'{self.project}.db')

        with con:
            con.execute('CREATE TABLE IF NOT EXISTS confs (_id INT PRIMARY KEY, _name VARCHAR(255))')
            con.execute('CREATE TABLE IF NOT EXISTS runs (_id INT PRIMARY KEY, _run_id INT, FOREIGN KEY (_run_id) REFERENCES confs (_id))')

        con.close()

    def start(self, run=None, config=None):

        return Run(project=self.project, run=run, config=config)

    def get(self, *columns):

        con = sqlite3.connect(f'{self.project}.db')

        columns = ",".join(columns)
        data = pd.read_sql_query(f"SELECT _id,{columns} FROM runs", con)

        return data


class Run:

    def __init__(self, project, run=None, config=None):

        self.path = f'{project}.db'

        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row

        cur = con.cursor()

        if config is not None:

            # Retrieve existing columns
            columns = []
            for column in cur.execute('PRAGMA table_info(confs)'):
                columns.append(column['name'])

            # Add missing columns
            for key in config.keys():
                if key not in columns:
                    # TODO: unsafe
                    cur.execute(f'ALTER TABLE confs ADD {key}')  # REAL?

            # TODO: unsafe add statistics
            columns = ",".join(config.keys())
            values = "','".join(map(str, config.values()))
            cur.execute(f"INSERT INTO confs ({columns}) VALUES ('{values}')")

        else:

            # TODO: check
            cur.execute('INSERT INTO confs () VALUES ()')

        self.run_id = cur.lastrowid

        cur.execute(f'UPDATE confs SET _name = (?) WHERE _id = (?)',
                    (str(self.run_id), self.run_id))

        con.commit()
        con.close()

    def log(self, statistics):

        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row

        cur = con.cursor()

        columns = []
        for column in cur.execute('PRAGMA table_info(runs)'):
            columns.append(column['name'])

        for key in statistics.keys():
            if key not in columns:
                # TODO: unsafe
                cur.execute(f'ALTER TABLE runs ADD {key} REAL')

        # TODO: unsafe add logs
        columns = ",".join(statistics.keys())
        values = "','".join(map(str, statistics.values()))
        cur.execute(f"INSERT INTO runs (_run_id,{columns}) "
                    f"VALUES ('{self.run_id}','{values}')")

        con.commit()
        con.close()

    def get(self, *columns):

        con = sqlite3.connect(self.path)

        columns = ",".join(columns)
        data = pd.read_sql_query(f"SELECT _id,{columns} FROM runs "
                                 f"WHERE _run_id = '{self.run_id}'", con)

        return data
