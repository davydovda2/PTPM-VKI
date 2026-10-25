import unittest

from main import Converter


class TestConverter(unittest.TestCase):

    def test_positive_large(self):
        self.assertEqual(Converter.do(100.7), 1000)
        self.assertEqual(Converter.do(100.8), 1000)
        self.assertEqual(Converter.do(101.0), 1000)
        self.assertEqual(Converter.do(500.5), 1000)
        self.assertEqual(Converter.do(10000.0), 1000)

    def test_positive_small(self):
        self.assertEqual(Converter.do(0.1), 0)
        self.assertEqual(Converter.do(0.5), 0)
        self.assertEqual(Converter.do(0.9), 0)
        self.assertEqual(Converter.do(1.0), 1)
        self.assertEqual(Converter.do(1.5), 1)
        self.assertEqual(Converter.do(50.7), 50)
        self.assertEqual(Converter.do(99.9), 99)
        self.assertEqual(Converter.do(100.6), 100)

    def test_zero(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_zero_negative(self):
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    def test_negative_in_range(self):
        self.assertEqual(Converter.do(-0.1), -5)
        self.assertEqual(Converter.do(-0.5), -5)
        self.assertEqual(Converter.do(-0.9), -5)
        self.assertEqual(Converter.do(-1.0), -6)
        self.assertEqual(Converter.do(-1.5), -6)
        self.assertEqual(Converter.do(-15.7), -20)
        self.assertEqual(Converter.do(-30.4), -35)

    def test_negative_large(self):
        self.assertEqual(Converter.do(-30.5), -2000)
        self.assertEqual(Converter.do(-31.0), -2000)
        self.assertEqual(Converter.do(-100.0), -2000)
        self.assertEqual(Converter.do(-1000.5), -2000)

    def test_boundary_100_7(self):
        self.assertEqual(Converter.do(100.6), 100)
        self.assertEqual(Converter.do(100.7), 1000)

    def test_boundary_neg_30(self):
        self.assertEqual(Converter.do(-30.4), -35)
        self.assertEqual(Converter.do(-30.5), -2000)


if __name__ == "__main__":
    unittest.main()