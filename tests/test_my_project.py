import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from my_project import solve


class TestSolve(unittest.TestCase):
    def test_equilateral_triangle_type(self):
        kind, coords = solve('5', '5', '5')
        self.assertEqual(kind, 'равносторонний')

    def test_isosceles_ab(self):
        kind, coords = solve('6', '6', '10')
        self.assertEqual(kind, 'равнобедренный')

    def test_isosceles_ac(self):
        kind, coords = solve('5', '6', '5')
        self.assertEqual(kind, 'равнобедренный')

    def test_isosceles_bc(self):
        kind, coords = solve('6', '5', '5')
        self.assertEqual(kind, 'равнобедренный')

    def test_scalene(self):
        kind, coords = solve('7', '8', '9')
        self.assertEqual(kind, 'разносторонний')

    def test_right_angled(self):
        kind, coords = solve('3', '4', '5')
        self.assertEqual(kind, 'разносторонний')

    def test_float_input(self):
        kind, coords = solve('1.5', '2.0', '2.5')
        self.assertEqual(kind, 'разносторонний')

    def test_large_values(self):
        kind, coords = solve('100', '100', '100')
        self.assertEqual(kind, 'равносторонний')

    def test_small_positive(self):
        kind, coords = solve('0.5', '0.5', '0.5')
        self.assertEqual(kind, 'равносторонний')

    def test_not_triangle_degenerate_sum_equal(self):
        kind, coords = solve('2', '2', '4')
        self.assertEqual(kind, 'не треугольник')

    def test_not_triangle_degenerate_just_equal(self):
        kind, coords = solve('5', '5', '10')
        self.assertEqual(kind, 'не треугольник')

    def test_not_triangle_sum_less(self):
        kind, coords = solve('1', '1', '5')
        self.assertEqual(kind, 'не треугольник')

    def test_not_triangle_very_stretched(self):
        kind, coords = solve('1', '1', '3')
        self.assertEqual(kind, 'не треугольник')

    def test_zero_side(self):
        kind, coords = solve('0', '2', '2')
        self.assertEqual(kind, 'не треугольник')

    def test_negative_side(self):
        kind, coords = solve('-1', '2', '2')
        self.assertEqual(kind, 'не треугольник')

    def test_all_zeros(self):
        kind, coords = solve('0', '0', '0')
        self.assertEqual(kind, 'не треугольник')

    def test_invalid_strings(self):
        kind, coords = solve('abc', '2', '3')
        self.assertEqual(kind, '')
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_partial_invalid(self):
        kind, coords = solve('1', 'b', '3')
        self.assertEqual(kind, '')
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_empty_strings(self):
        kind, coords = solve('', '', '')
        self.assertEqual(kind, '')
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_mixed_float_valid(self):
        kind, coords = solve('1.0', '2.5', '3.0')
        self.assertEqual(kind, 'разносторонний')
