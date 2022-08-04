import re
import shutil
import filecmp
import sqlite3
import pandas as pd

from pathlib import Path


MLOG_DIR = Path("./mlog")
MLOG_DB = MLOG_DIR / "mlog.db"
KEY_FORMAT = "[a-zA-Z][a-zA-Z0-9_]*"
GET_FORMAT = "[a-zA-Z_][a-zA-Z0-9_]*"

SQL_CREATE_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS runs (
    _run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    _name VARCHAR(255)
)
"""

SQL_CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS logs (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    _run_id INT,
    FOREIGN KEY (_run_id) REFERENCES runs (_run_id)
)
"""

def start(run=None, config=None, save=None):
    return Run(run=run, config=config, save=save)


def lst(*columns, filters=None):

    if filters is not None:
        raise NotImplementedError

    con = sqlite3.connect(MLOG_DB)
    data = pd.read_sql_query(f"SELECT * FROM runs", con)
    con.close()

    return data.set_index('_run_id')


def get(*columns, **filters):

    # TODO: implement filters with inequalities, etc

    con = sqlite3.connect(MLOG_DB)

    # Retrieve existing columns
    with con:
        cols = (
            [col[1] for col in con.execute("PRAGMA table_info(logs)")] +
            [col[1] for col in con.execute("PRAGMA table_info(runs)")])

    if columns:
        for column in columns:
            if not re.fullmatch(GET_FORMAT, column):
                raise ValueError(
                    f"Column '{column}' does not use format '{GET_FORMAT}'")

        columns = list(columns)
        columns.append('_id')
        columns = ",".join(columns)
    else:
        columns='*'

    if filters:
        for key, val in filters.items():
            if not re.fullmatch(GET_FORMAT, key):
                raise ValueError(
                    f"Filter '{key}' does not use format '{GET_FORMAT}'")

            if key not in cols:
                raise ValueError(
                    f"Filter '{key}' not in columns.")

            if not re.fullmatch(GET_FORMAT, str(val)):
                try:
                    float(val)
                except ValueError:
                    raise ValueError(
                        f"Value '{val}' for column '{key}' is not a number "
                        f"nor a valid run name")

        filters = ' AND '.join(f"{k} = {v}" for k, v in filters.items())
    else:
        filters='1'

    data = pd.read_sql_query(f"SELECT {columns} FROM logs NATURAL JOIN runs "
                             f"WHERE {filters}", con)

    con.close()

    return data.set_index('_id')


def delete(run_id):

    con = sqlite3.connect(MLOG_DB)
    with con:
        con.execute('DELETE FROM logs WHERE _run_id = ?', (str(run_id),))
        con.execute('DELETE FROM runs WHERE _run_id = ?', (str(run_id),))
        save_dir = MLOG_DIR / str(run_id)
        if save_dir.is_symlink():
            save_dir.unlink()

    con.close()


class Run:

    def __init__(self, run=None, config=None, save=None):

        if run is not None and not re.fullmatch(KEY_FORMAT, run):
            raise ValueError(
                f"Run name '{run}' does not use format '{KEY_FORMAT}'")

        con = sqlite3.connect(MLOG_DB)
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

        # Save files
        if save is not None:

            save_dir = MLOG_DIR / str(self.run_id)
            save_dir.mkdir()

            for file in Path('.').glob(save):
                shutil.copy(file, save_dir)

            # Symlink previous save if identical
            prev_save_dir = MLOG_DIR / (str(self.run_id - 1))
            if prev_save_dir.is_symlink():
                prev_save_dir = prev_save_dir.readlink()

            diff = filecmp.dircmp(save_dir, prev_save_dir)

            if prev_save_dir.is_dir() and not diff.diff_files:
                shutil.rmtree(save_dir)
                save_dir.symlink_to(prev_save_dir, target_is_directory=True)

    def log(self, **logs):

        con = sqlite3.connect(MLOG_DB)

        with con:
            # Retrieve existing columns
            cols = [col[1] for col in con.execute("PRAGMA table_info(logs)")]

            # Check columns and values format and add missing columns
            for key, val in logs.items():

                if not re.fullmatch(KEY_FORMAT, key):
                    raise ValueError(
                        f"Column '{key}' does not use format '{KEY_FORMAT}'")

                if key not in cols:
                    con.execute(f"ALTER TABLE logs ADD {key} REAL")

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
            con.execute(f"INSERT INTO logs ({cols}) VALUES ({vals})", logs)

        # Remove run id
        logs.pop('_run_id')

        con.commit()
        con.close()

    def get(self, *columns):
        return get(*columns, _run_id=self.run_id)
