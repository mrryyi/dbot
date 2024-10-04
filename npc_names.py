import sqlite3
from enum import IntEnum
from log import *
from dataclasses import dataclass
from typing import List, Optional

conn = sqlite3.connect('npc_names.db')

cursor = conn.cursor()


#region Datamodel definition
cursor.execute('''
CREATE TABLE IF NOT EXISTS npc_names (
    id INTEGER PRIMARY KEY,
    name varchar(255),
    taken BOOL DEFAULT 0,
    datetime_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    datetime_taken DATETIME NULL DEFAULT NULL
)
''')

cursor.execute('''
CREATE UNIQUE INDEX IF NOT EXISTS ux_npc_names_name ON npc_names(name);
''')

conn.commit()

# Match against SQL data model.
@dataclass
class NpcName:
    id: int
    name: str
    taken: bool
    datetime_created: str
    datetime_taken: Optional[str]  # Optional, since it can be NULL
#endregion

#region SQL result helpers.
class db_operation_result(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    ALREADY_EXISTS = 2
    NO_QUERY_RESULT = 3

@dataclass
class FetchResult:
    status: db_operation_result
    error_message: str = None
#endregion

#region SQL Inserts
def insert_singular_name(name: str) -> db_operation_result:
    try:
        cursor.execute('''
        INSERT INTO npc_names (name)
        VALUES (?)
        ''', (name,))

        conn.commit()

    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            return db_operation_result.ALREADY_EXISTS
        else:
            log_exception_local(e)
            return db_operation_result.GENERAL_ERROR
    except Exception as e:
        log_exception_local(e)

    return db_operation_result.SUCCESS
#endregion

#region SQL Gets
@dataclass
class NameFetchResult(FetchResult):
    npc_name: NpcName = None

def get_random_untaken_name() -> NameFetchResult:
    try:
        cursor.execute('''
        SELECT id, name, taken, datetime_created, datetime_taken
        FROM npc_names
        WHERE taken = 0
        ORDER BY RANDOM()
        LIMIT 1
        ''')
        row = cursor.fetchone()

        if row is None:
            return NameFetchResult(db_operation_result.NO_QUERY_RESULT)
        
        return NameFetchResult(db_operation_result.SUCCESS, npc_name=NpcName(*row))
        
    except Exception as e:
        log_exception_local(e)
        return NameFetchResult(db_operation_result.GENERAL_ERROR, error_message=str(e))

@dataclass
class NamesFetchResult(FetchResult):
    npc_names: List[NpcName] = None

def get_all_untaken_names() -> NamesFetchResult:
    try:
        cursor.execute('SELECT id, name, taken, datetime_created, datetime_taken FROM npc_names')
        rows = cursor.fetchall()

        if rows is None:
            return NamesFetchResult(db_operation_result.NO_QUERY_RESULT)
        
        return NamesFetchResult(db_operation_result.SUCCESS, npc_names=[NpcName(*row) for row in rows])
        
    except Exception as e:
        log_exception_local(e)
        return NamesFetchResult(db_operation_result.GENERAL_ERROR, error_message=str(e))
#endregion