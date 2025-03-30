import unittest

from app.data_ingestor import DataIngestor  

class TestWebServer(unittest.TestCase):
    def test_upper(self):
        print("Running test_upper...")
        self.assertEqual('foo'.upper(), 'FOO')

    def test_upper_2(self):
        print("Running test_upper...")
        self.assertEqual('foo'.upper(), 'FOO')

    
if __name__ == '__main__':
    print("Starting tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebServer)
unittest.TextTestRunner(verbosity=2).run(suite)

