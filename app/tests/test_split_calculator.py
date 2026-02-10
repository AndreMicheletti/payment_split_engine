from decimal import Decimal
from django.test import TestCase
from app.services.split_service import SplitService


class SplitCalculatorTestCase(TestCase):
    def test_split_calculator_simple(self):
        total_amount = Decimal("125.00")
        fee_percent = Decimal("20.00")
        splits = [
            {"recipient_id": "A", "percent": 70},
            {"recipient_id": "B", "percent": 30},
        ]

        result = SplitService.calculate(total_amount, fee_percent, splits)
        self.assertEqual(result["fee_amount"], Decimal("25.00"))
        self.assertEqual(result["net_amount"], Decimal("100.00"))
        self.assertEqual(len(result["receivables"]), 2)
        print(result["receivables"])
        self.assertEqual(
            sum(x["amount"] for x in result["receivables"]), result["net_amount"]
        )

    def test_split_calculator_cents_distribute(self):
        total_amount = Decimal("125.00")
        fee_percent = Decimal("20.00")
        splits = [
            {"recipient_id": "A", "percent": 33},
            {"recipient_id": "B", "percent": 33},
            {"recipient_id": "C", "percent": 33},
        ]

        result = SplitService.calculate(total_amount, fee_percent, splits)
        fee_amount = result["fee_amount"]
        net_amount = result["net_amount"]
        receivables = result["receivables"]

        assert fee_amount == Decimal("25.00")
        assert net_amount == Decimal("100.00")
        assert len(receivables) == 3
        print(receivables)
        assert sum(x["amount"] for x in receivables) == net_amount

        [*normal_ones, lucky_one] = receivables
        assert all(x["amount"] == Decimal("33.33") for x in normal_ones)
        assert lucky_one["amount"] == Decimal("33.34")
