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

    #region insert_singular_name
    def test_insert_singular_name(self):
        result = self.db.insert_singular_name('TestName')
        self.assertEqual(result, db_operation_result.SUCCESS)
        # Verify that the name exists in the database
        res = self.db.get_all_names()
        self.assertEqual(len(res.npc_names), 1)
        self.assertEqual(res.npc_names[0].name, 'TestName')
    
    def test_insert_singular_name_duplicate(self):
        result = self.db.insert_singular_name('TestName')
        self.assertEqual(result, db_operation_result.SUCCESS)
        result = self.db.insert_singular_name('TestName')
        self.assertEqual(result, db_operation_result.ALREADY_EXISTS)
    
    def test_insert_singular_name_empty_string(self):
        result = self.db.insert_singular_name('')
        self.assertEqual(result, db_operation_result.GENERAL_ERROR)
    
    def test_insert_singular_name_none_value(self):
        result = self.db.insert_singular_name(None)
        self.assertEqual(result, db_operation_result.GENERAL_ERROR)
    
    def test_insert_singular_name_special_characters(self):
        result = self.db.insert_singular_name('TestName!@#$%^&*()')
        self.assertEqual(result, db_operation_result.SUCCESS)
        # Verify that the name exists in the database
        res = self.db.get_all_names()
        self.assertEqual(len(res.npc_names), 1)
        self.assertEqual(res.npc_names[0].name, 'TestName!@#$%^&*()')
    #endregion
    #region get_random_untaken_name
    def test_get_random_untaken_name(self):
        self.db.insert_singular_name('TestName')
        res = self.db.get_random_untaken_name()
        self.assertEqual(res.status, db_operation_result.SUCCESS)
        self.assertEqual(res.npc_name.name, 'TestName')
    
    def test_get_random_untaken_name_no_untaken_names(self):
        res = self.db.get_random_untaken_name()
        self.assertEqual(res.status, db_operation_result.NO_QUERY_RESULT)
    
    def test_get_random_untaken_name_duplicate(self):
        self.db.insert_singular_name('TestName')
        self.db.get_random_untaken_name_and_take_it()
        res = self.db.get_random_untaken_name()
        self.assertEqual(res.status, db_operation_result.NO_QUERY_RESULT)
    
    def test_get_random_untaken_name_special_characters(self):
        self.db.insert_singular_name('TestName!@#$%^&*()')
        res = self.db.get_random_untaken_name()
        self.assertEqual(res.status, db_operation_result.SUCCESS)
        self.assertEqual(res.npc_name.name, 'TestName!@#$%^&*()')
    #endregion
    #region get_random_untaken_name_and_take_it
    def test_get_random_untaken_name_and_take_it_success(self):
        self.db.insert_singular_name('TestName')
        res = self.db.get_random_untaken_name_and_take_it()
        self.assertEqual(res.status, db_operation_result.SUCCESS)
        self.assertEqual(res.npc_name.name, 'TestName')
        # Verify the name is now marked as taken
        name_res = self.db.get_all_taken_names()
        self.assertEqual(len(name_res.npc_names), 1)
        self.assertEqual(name_res.npc_names[0].name, 'TestName')

    def test_get_random_untaken_name_and_take_it_state_change(self):
        self.db.insert_singular_name('TestName')
        self.db.get_random_untaken_name_and_take_it()
        res = self.db.get_random_untaken_name_and_take_it()
        self.assertEqual(res.status, db_operation_result.NO_QUERY_RESULT)
    
    def test_get_random_untaken_name_and_take_it_no_names(self):
        res = self.db.get_random_untaken_name_and_take_it()
        self.assertEqual(res.status, db_operation_result.NO_QUERY_RESULT)
    #endregion
    #region get_all_names
    def test_get_all_names(self):
        test_names = ['TestName', 'TestName2', 'TestName3']
        self.db.insert_singular_name(test_names[0])
        self.db.insert_singular_name(test_names[1])
        self.db.insert_singular_name(test_names[2])
        res = self.db.get_all_names()
        self.assertEqual(len(res.npc_names), 3)

        self.assertIn(res.npc_names[0].name, test_names)
        self.assertIn(res.npc_names[1].name, test_names)
        self.assertIn(res.npc_names[2].name, test_names)
    
    def test_get_all_names_no_names(self):
        res = self.db.get_all_names()
        self.assertEqual(res.status, db_operation_result.NO_QUERY_RESULT)
    
    def test_get_all_names_special_characters(self):
        test_name = 'TestName!@#$%^&*()'
        self.db.insert_singular_name(test_name)
        res = self.db.get_all_names()
        self.assertEqual(len(res.npc_names), 1)
        self.assertEqual(res.npc_names[0].name, test_name)
    
    def test_get_all_names_state_change(self):
        test_names = ['TestName', 'TestName2', 'TestName3']
        self.db.insert_singular_name(test_names[0])
        self.db.insert_singular_name(test_names[1])
        self.db.insert_singular_name(test_names[2])
        self.db.get_random_untaken_name_and_take_it()
        res = self.db.get_all_names()
        self.assertEqual(len(res.npc_names), 3)
    #endregion
    #region get_all_taken_names
    def test_get_all_taken_names(self):
        test_names = ['TestName', 'TestName2', 'TestName3']
        self.db.insert_singular_name(test_names[0])
        self.db.insert_singular_name(test_names[1])
        self.db.insert_singular_name(test_names[2])
        self.db.get_random_untaken_name_and_take_it()
        res = self.db.get_all_taken_names()
        self.assertEqual(len(res.npc_names), 1)
        self.assertIn(res.npc_names[0].name, test_names)
    
    def test_get_all_taken_names_no_results(self):
        res = self.db.get_all_taken_names()
        self.assertEqual(res.status, db_operation_result.NO_QUERY_RESULT)
    #endregion
    #region get_all_untaken_names
    def test_get_all_untaken_names(self):
        test_names = ['TestName', 'TestName2', 'TestName3']
        self.db.insert_singular_name(test_names[0])
        self.db.insert_singular_name(test_names[1])
        self.db.insert_singular_name(test_names[2])
        self.db.get_random_untaken_name_and_take_it()
        res = self.db.get_all_untaken_names()
        self.assertEqual(len(res.npc_names), 2)
        self.assertIn(res.npc_names[0].name, test_names)
        self.assertIn(res.npc_names[1].name, test_names)
    
    def test_get_all_untaken_names_no_results(self):
        res = self.db.get_all_untaken_names()
        self.assertEqual(res.status, db_operation_result.NO_QUERY_RESULT)
    #endregion

if __name__ == '__main__':
    unittest.main()