import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from delivery_service import calculate_delivery_cost


class TestDeliveryCost(unittest.TestCase):
    def test_basic_ordinary(self):
        cost, date = calculate_delivery_cost(1.0, 500, 'обычный')
        self.assertEqual((cost, date), (2700, '2026-09-04'))

    def test_weight_mid_increase(self):
        cost, date = calculate_delivery_cost(10.0, 500, 'обычный')
        self.assertEqual((cost, date), (3240, '2026-09-04'))

    def test_weight_heavy_increase(self):
        cost, date = calculate_delivery_cost(20.0, 500, 'обычный')
        self.assertEqual((cost, date), (4050, '2026-09-04'))

    def test_fragile(self):
        cost, date = calculate_delivery_cost(1.0, 500, 'хрупкий')
        self.assertEqual((cost, date), (3000, '2026-09-04'))

    def test_dangerous(self):
        cost, date = calculate_delivery_cost(1.0, 500, 'опасный')
        self.assertEqual((cost, date), (3700, '2026-09-04'))

    def test_express(self):
        cost, date = calculate_delivery_cost(1.0, 500, 'обычный', is_express=True)
        self.assertEqual((cost, date), (1350, '2026-09-03'))

    def test_weight_too_small(self):
        cost, date = calculate_delivery_cost(0.05, 500, 'обычный')
        self.assertEqual((cost, date), (-1, '0000-00-00'))

    def test_weight_too_large(self):
        cost, date = calculate_delivery_cost(50.1, 500, 'обычный')
        self.assertEqual((cost, date), (-1, '0000-00-00'))

    def test_invalid_type(self):
        cost, date = calculate_delivery_cost(1.0, 500, 'неизвестный')
        self.assertEqual((cost, date), (-1, '0000-00-00'))

    def test_distance_invalid(self):
        cost, date = calculate_delivery_cost(1.0, 0, 'обычный')
        self.assertEqual((cost, date), (-1, '0000-00-00'))
