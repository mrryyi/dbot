import sqlite3
import unittest
from npc_names import * 

class TestNpcNamesDatabase(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database
        self.test_conn = sqlite3.connect(':memory:')
        # Reset the singleton and initialize with test database
        self.db = get_db_instance_npc_names(self.test_conn,  reset_instance=True)

    def tearDown(self):
        self.test_conn.close()
        # Reset the singleton after each test
        get_db_instance_npc_names(reset_instance=True)

    def test_insert_singular_name(self):
        result = self.db.insert_singular_name('TestName')
        self.assertEqual(result, db_operation_result.GENERAL_ERROR)
        # Further assertions...
    
if __name__ == '__main__':
    unittest.main()