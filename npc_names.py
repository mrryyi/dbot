import sqlite3
from log import *
from typing import List, Optional
from sql_base import *

# Match against SQL data model.
@dataclass
class NpcName:
    id: int
    name: str
    taken: bool
    datetime_created: str
    datetime_taken: Optional[str]  # Optional, since it can be NULL

#region SQL result helpers.
@dataclass
class NameFetchResult(FetchResult):
    npc_name: NpcName = None

@dataclass
class NamesFetchResult(FetchResult):
    npc_names: List[NpcName] = None
#endregion

class NpcNamesDatabase:
    _instance = None  # Class-level attribute for singleton

    def __new__(cls, db_connection=None, reset_instance=False):
        if cls._instance is None or reset_instance:
            cls._instance = super(NpcNamesDatabase, cls).__new__(cls)
            cls._instance._initialize_database(db_connection)
        return cls._instance

    def _initialize_database(self, db_connection=None):
        if db_connection is None:
            self.conn = sqlite3.connect('npc_names.db')
        else:
            self.conn = db_connection
        
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._run_initial_sql()

    def _run_initial_sql(self):
        with open('sql\\table_npc_names.sql', 'r') as file:
            sql_script = file.read()
        self.cursor.executescript(sql_script)
        self.conn.commit()

#region SQL Inserts
    def insert_singular_name(self, name: str) -> db_operation_result:
        if not name:
            return db_operation_result.GENERAL_ERROR

        try:
            self.cursor.execute('''
            INSERT INTO npc_names (name)
            VALUES (?)
            ''', (name,))

            self.conn.commit()

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
    def get_random_untaken_name(self) -> NameFetchResult:
        try:
            self.cursor.execute('''
            SELECT id, name, taken, datetime_created, datetime_taken
            FROM npc_names
            WHERE taken = 0
            ORDER BY RANDOM()
            LIMIT 1
            ''')
            row = self.cursor.fetchone()

            if row is None:
                return NameFetchResult(db_operation_result.NO_QUERY_RESULT)
            
            return NameFetchResult(db_operation_result.SUCCESS, npc_name=NpcName(*row))
            
        except Exception as e:
            log_exception_local(e)
            return NameFetchResult(db_operation_result.GENERAL_ERROR, error_message=str(e))

    def get_random_untaken_name_and_take_it(self) -> NameFetchResult:
        try:
            self.cursor.execute('''
            SELECT id, name, taken, datetime_created, datetime_taken
            FROM npc_names
            WHERE taken = 0
            ORDER BY RANDOM()
            LIMIT 1
            ''')
            row = self.cursor.fetchone()

            if row is None:
                return NameFetchResult(db_operation_result.NO_QUERY_RESULT)
            
            id: int = row['id']
            
            self.cursor.execute('''
            UPDATE npc_names
            SET taken = 1, datetime_taken = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (id,))
            
            self.conn.commit()
            
            return NameFetchResult(db_operation_result.SUCCESS, npc_name=NpcName(*row))
            
        except Exception as e:
            log_exception_local(e)
            return NameFetchResult(db_operation_result.GENERAL_ERROR, error_message=str(e))


    def fetch_names(self, query_condition: str = "") -> NamesFetchResult:
        try:
            base_query = 'SELECT id, name, taken, datetime_created, datetime_taken FROM npc_names'
            if query_condition:
                query = f"{base_query} WHERE {query_condition}"
            else:
                query = base_query
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            if not rows:
                return NamesFetchResult(db_operation_result.NO_QUERY_RESULT)
            
            return NamesFetchResult(db_operation_result.SUCCESS, npc_names=[NpcName(*row) for row in rows])

        except Exception as e:
            log_exception_local(e)
            return NamesFetchResult(db_operation_result.GENERAL_ERROR, error_message=str(e))

    def get_all_names(self) -> NamesFetchResult:
        return self.fetch_names()

    def get_all_taken_names(self) -> NamesFetchResult:
        return self.fetch_names("taken != 0")

    def get_all_untaken_names(self) -> NamesFetchResult:
        return self.fetch_names("taken = 0")
#endregion

def get_db_instance_npc_names(db_connection=None, reset_instance=False):
    return NpcNamesDatabase(db_connection, reset_instance)