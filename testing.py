from marvel_main import app
import unittest

class MarvelAPITests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass 

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        # create  test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True 

    def tearDown(self):
        pass
    
    def test_status_code(self):
        path = '/marvel/characters/583560'
        result = self.app.get(path)
        self.assertEqual(result.status_code, 200)

    # TODO: Create tests to validate GET results and
    # confirm that the parameters (including sortby and
    # orderby) were applied correctly.
    

if __name__ == '__main__':
    unittest.main()