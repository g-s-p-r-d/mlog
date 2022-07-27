import os
import re
import sqlite3

import pandas as pd


# TODO: cli: merge several database?
# TODO: propose code caching and outputs saving
# TODO: add local .mlogconfig file
#   - db path
#   - remotes
#   - source files
#   - up files
#   - down files


class Project:

    def __init__(self, project=None):

        self.project = project if project is not None else 'project'
        if not re.fullmatch('[a-zA-Z_]+', self.project):
            raise ValueError("Project name can only contain letters and _")

        con = sqlite3.connect(f'{self.project}.db')

        with con:

            con.execute('''
                CREATE TABLE IF NOT EXISTS confs (
                    _id INTEGER PRIMARY KEY AUTOINCREMENT,
                    _name VARCHAR(255))
                ''')

            con.execute('''
                CREATE TABLE IF NOT EXISTS runs (
                    _id INTEGER PRIMARY KEY AUTOINCREMENT,
                    _run_id INT,
                    FOREIGN KEY (_run_id) REFERENCES confs (_id))
                ''')

        con.close()

    def start(self, run=None, config=None):

        return Run(project=self.project, run=run, config=config)

    def get(self, *columns):

        con = sqlite3.connect(f'{self.project}.db')

        for column in columns:
            if not re.fullmatch('[a-zA-Z_]+', column):
                raise ValueError("Column name can only contain letters and _")

        columns = ",".join(columns)
        # TODO: catch errors with empty tables
        data = pd.read_sql_query(f"SELECT _id,{columns} FROM runs", con)

        return data


class Run:

    def __init__(self, project, run=None, config=None):

        if not re.fullmatch('[a-zA-Z_]+', project):
            raise ValueError("Project name can only contain letters and _")
        if not re.fullmatch('[a-zA-Z_]+', run):
            raise ValueError("Run name can only contain letters and _")

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
                    cur.execute(f'ALTER TABLE confs ADD {key}')

            # Add statistics
            columns = ",".join(config.keys())
            values = "','".join(map(str, config.values()))
            # TODO: unsafe
            cur.execute(f"INSERT INTO confs ({columns}) VALUES ('{values}')")

        else:
            # TODO: check
            cur.execute('INSERT INTO confs () VALUES ()')

        self.run_id = cur.lastrowid

        cur.execute(f'UPDATE confs SET _name = (?) WHERE _id = (?)',
                    (str(self.run_id), self.run_id))

        con.commit()
        con.close()

    def log(self, **statistics):

        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row

        cur = con.cursor()

        # Check column names and values
        for key, val in statistics.items():
            if not re.fullmatch('[a-zA-Z_]+', key):
                raise ValueError("Column name can only contain letters and _")
            try:
                float(val)
            except ValueError:
                raise ValueError("Only numbers can be logged")

        # Retrieve existing columns
        columns = []
        for column in cur.execute('PRAGMA table_info(runs)'):
            columns.append(column['name'])

        # Add missing columns
        for key in statistics.keys():
            if key not in columns:
                # TODO: unsafe
                cur.execute(f'ALTER TABLE runs ADD {key} REAL')

        # Add logs
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
