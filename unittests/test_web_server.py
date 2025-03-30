import unittest
from app.data_ingestor import DataIngestor

class TestWebServer(unittest.TestCase):
    
    def test_upper(self):
        """Test the upper case functionality."""
        print("Running test_upper...")

        # Describing the first test (multiplication)
        self.describe("Upper Case Tests")
        
        # Sub-test 1
        self.it("should convert 'foo' to 'FOO'", lambda: self.assertEqual('foo'.upper(), 'FOO'))

        # Sub-test 2
        self.it("should convert 'bar' to 'BAR'", lambda: self.assertEqual('bar'.upper(), 'BAR'))

    def test_upper_2(self):
        """Test the upper case functionality again."""
        print("Running test_upper_2...")

        # Describing the second test (division)
        self.describe("Second Upper Case Tests")

        # Sub-test 1
        self.it("should convert 'hello' to 'HELLO'", lambda: self.assertEqual('hello'.upper(), 'HELLO'))

        # Sub-test 2
        self.it("should convert 'world' to 'WORLD'", lambda: self.assertEqual('world'.upper(), 'WORLD'))

    # Custom method to describe test sections
    def describe(self, description):
        """Print description for a group of related tests."""
        print(f"\n{description}:")

    # Custom method to describe individual tests
    def it(self, description, test_func):
        """Print description for a single test and execute the test."""
        print(f"  - {description}")
        test_func()  # Execute the actual test function
    
if __name__ == '__main__':
    print("Starting tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebServer)
    unittest.TextTestRunner(verbosity=2).run(suite)
