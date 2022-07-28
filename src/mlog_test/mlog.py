import re
import sqlite3
import pandas as pd

from pathlib import Path


MLOG_DIR = Path("./mlog")
MLOG_DB = MLOG_DIR / "mlog.db"
KEY_FORMAT = "[a-zA-Z][a-zA-Z0-9_]*"
GET_FORMAT = "[a-zA-Z_][a-zA-Z0-9_]*"

SQL_CREATE_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS runs (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    _name VARCHAR(255),
    _source VARCHAR(255)
)
"""

SQL_CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS logs (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    _run_id INT,
    FOREIGN KEY (_run_id) REFERENCES runs (_id)
)
"""

SQL_CREATE_REMOTES_TABLE = """
CREATE TABLE IF NOT EXISTS remotes (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE,
    path VARCHAR(255)
)
"""


def start(run=None, config=None, save=None):
    return Run(run=run, config=config, save=save)


def get(*columns, filters=None):

    con = sqlite3.connect(MLOG_DB)

    for column in columns:
        if not re.fullmatch(GET_FORMAT, column):
            raise ValueError(
                f"Column '{column}' does not use format '{GET_FORMAT}'")

    columns = list(columns)
    columns.append('_id')
    columns = ",".join(columns)

    data = pd.read_sql_query(f"SELECT {columns} FROM logs", con)

    return data.set_index('_id')


def add(args):

    con = sqlite3.connect(MLOG_DB)

    with con:
        con.execute(f"INSERT INTO remotes (name, path) VALUES (?, ?)",
                    (args.remote, args.path))

    con.close()


def remotes(args):

    con = sqlite3.connect(MLOG_DB)

    with con:
        data = con.execute(f"SELECT name, path FROM remotes")
        for row in data:
            print(f"{row[0]}\t{row[1]}")

    con.close()


def remove(args):

    con = sqlite3.connect(MLOG_DB)

    with con:
        con.execute(f"DELETE FROM remotes WHERE name = ?", args.remote)

    con.close()


def sync(args):

    raise NotImplementedError


class Run:

    def __init__(self, run=None, config=None, save=None):

        MLOG_DIR.mkdir(parents=True, exist_ok=True)

        if save is not None:
            raise NotImplementedError

        if not re.fullmatch(KEY_FORMAT, run):
            raise ValueError(
                f"Run name '{run}' does not use format '{KEY_FORMAT}'")

        con = sqlite3.connect(MLOG_DB)

        with con:
            con.execute(SQL_CREATE_RUNS_TABLE)
            con.execute(SQL_CREATE_LOGS_TABLE)
            con.execute(SQL_CREATE_REMOTES_TABLE)

        # TODO: with con ?
        cur = con.cursor()

        if config:

            # Retrieve existing columns
            cols = [col[1] for col in cur.execute('PRAGMA table_info(runs)')]

            # Check columns format and add missing columns
            for key in config.keys():

                if not re.fullmatch(KEY_FORMAT, key):
                    raise ValueError(
                        f"Column '{key}' does not use format '{KEY_FORMAT}'")

                if key not in cols:
                    cur.execute(f"ALTER TABLE runs ADD {key}")

            # Add name
            config["_name"] = run

            # Add configs
            cols = ",".join(config.keys())
            vals = ":" + ",:".join(config.keys())
            cur.execute(f"INSERT INTO runs ({cols}) VALUES ({vals})", config)

            # Remove name
            config.pop("_name")

        else:
            cur.execute("INSERT INTO runs DEFAULT VALUES")

        self.run_id = cur.lastrowid

        con.commit()
        con.close()

    def log(self, **logs):

        con = sqlite3.connect(MLOG_DB)
        cur = con.cursor()

        # Retrieve existing columns
        cols = [col[1] for col in cur.execute("PRAGMA table_info(logs)")]

        # Check columns and values format and add missing columns
        for key, val in logs.items():

            if not re.fullmatch(KEY_FORMAT, key):
                raise ValueError(
                    f"Column '{key}' does not use format '{KEY_FORMAT}'")

            if key not in cols:
                cur.execute(f"ALTER TABLE logs ADD {key} REAL")

            try:
                float(val)
            except ValueError:
                raise ValueError(
                    f"Value '{val}' for column '{key}' is not a number")

        # Add run id
        logs['_run_id'] = self.run_id

        # Add logs
        cols = ",".join(logs.keys())
        vals = ":" + ",:".join(logs.keys())
        cur.execute(f"INSERT INTO logs ({cols}) VALUES ({vals})", logs)

        # Remove run id
        logs.pop('_run_id')

        con.commit()
        con.close()

    def get(self, *columns):
        # TODO: call get with appropriate filter

        con = sqlite3.connect(MLOG_DB)

        for column in columns:
            if not re.fullmatch(GET_FORMAT, column):
                raise ValueError(
                    f"Column '{column}' does not use format '{GET_FORMAT}'")

        columns = list(columns)
        columns.append('_id')
        columns = ",".join(columns)

        data = pd.read_sql_query(
            f"SELECT {columns} FROM logs WHERE _run_id = '{self.run_id}'", con)

        return data.set_index('_id')
