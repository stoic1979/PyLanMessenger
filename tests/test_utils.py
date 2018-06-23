import unittest
 
class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_sum1(self):
        self.assertEqual(3*4, 12)
 
    def test_sum2(self):
        self.assertEqual('abc'[1:], 'bc')
 
if __name__ == '__main__':
    unittest.main()
