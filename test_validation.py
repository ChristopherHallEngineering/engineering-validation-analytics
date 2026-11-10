import unittest
from validation import summarize

class ValidationTests(unittest.TestCase):
    def test_nominal_data(self):
        s=summarize([9.8,10.0,10.1,10.2],9.5,10.5)
        self.assertTrue(s.all_within_limits)
        self.assertEqual(s.failures,0)
        self.assertAlmostEqual(s.mean,10.025)
    def test_out_of_limit(self):
        s=summarize([10,10.1,11],9.5,10.5)
        self.assertEqual(s.failures,1)
        self.assertFalse(s.all_within_limits)
    def test_too_few(self):
        with self.assertRaises(ValueError): summarize([10],9,11)
    def test_nonfinite(self):
        with self.assertRaises(ValueError): summarize([10,float("nan")],9,11)
    def test_invalid_limits(self):
        with self.assertRaises(ValueError): summarize([10,11],12,9)

if __name__=="__main__":
    unittest.main()
