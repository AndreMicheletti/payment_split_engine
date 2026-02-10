from decimal import Decimal
from django.test import TestCase
from app.services.split_service import SplitService


class SplitCalculatorTestCase(TestCase):
    def _assert_split_case(self, case):
        result = SplitService.calculate(
            case["gross_amount"], case["fee_percent"], case["splits"]
        )
        fee_amount = result["fee_amount"]
        net_amount = result["net_amount"]
        receivables = result["receivables"]

        assert fee_amount == case["expected_fee"]
        assert net_amount == case["expected_net"]
        assert len(receivables) == len(case["expected_amounts"])
        assert sum(x["amount"] for x in receivables) == net_amount
        assert [x["amount"] for x in receivables] == case["expected_amounts"]

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
        self.assertEqual(
            sum(x["amount"] for x in result["receivables"]), result["net_amount"]
        )

    def test_split_calculator_cents_distribute(self):
        total_amount = Decimal("125.00")
        fee_percent = Decimal("20.00")
        splits = [
            {"recipient_id": "A", "percent": 33.33},
            {"recipient_id": "B", "percent": 33.33},
            {"recipient_id": "C", "percent": 33.34},
        ]

        result = SplitService.calculate(total_amount, fee_percent, splits)
        fee_amount = result["fee_amount"]
        net_amount = result["net_amount"]
        receivables = result["receivables"]

        assert fee_amount == Decimal("25.00")
        assert net_amount == Decimal("100.00")
        assert len(receivables) == 3
        assert sum(x["amount"] for x in receivables) == net_amount

        [*normal_ones, lucky_one] = receivables
        assert all(x["amount"] == Decimal("33.33") for x in normal_ones)
        assert lucky_one["amount"] == Decimal("33.34")

    def test_split_calculator_cents_distribute_parametrized(self):
        cases = [
            {
                "gross_amount": Decimal("10.00"),
                "fee_percent": Decimal("0.00"),
                "splits": [
                    {"recipient_id": "A", "percent": 99},
                    {"recipient_id": "B", "percent": 1},
                ],
                "expected_fee": Decimal("0.00"),
                "expected_net": Decimal("10.00"),
                "expected_amounts": [
                    Decimal("9.90"),
                    Decimal("0.10"),
                ],
            },
            {
                "gross_amount": Decimal("100.01"),
                "fee_percent": Decimal("0.00"),
                "splits": [
                    {"recipient_id": "A", "percent": 50},
                    {"recipient_id": "B", "percent": 50},
                ],
                "expected_fee": Decimal("0"),
                "expected_net": Decimal("100.01"),
                "expected_amounts": [
                    Decimal("50.00"),
                    Decimal("50.01"),
                ],
            },
            {
                "gross_amount": Decimal("100.07"),
                "fee_percent": Decimal("0.00"),
                "splits": [
                    {"recipient_id": "A", "percent": 50},
                    {"recipient_id": "B", "percent": 50},
                ],
                "expected_fee": Decimal("0"),
                "expected_net": Decimal("100.07"),
                "expected_amounts": [
                    Decimal("50.03"),
                    Decimal("50.04"),
                ],
            },
            {
                "gross_amount": Decimal("100.10"),
                "fee_percent": Decimal("0.00"),
                "splits": [
                    {"recipient_id": "A", "percent": 50},
                    {"recipient_id": "B", "percent": 23},
                    {"recipient_id": "C", "percent": 27},
                ],
                "expected_fee": Decimal("0"),
                "expected_net": Decimal("100.10"),
                "expected_amounts": [
                    Decimal("50.05"),
                    Decimal("23.02"),
                    Decimal("27.03"),
                ],
            },
        ]

        for case in cases:
            with self.subTest(gross_amount=case["gross_amount"]):
                self._assert_split_case(case)
