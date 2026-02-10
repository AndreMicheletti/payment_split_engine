from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from typing import List, Dict

class SplitService:
    @staticmethod
    def calculate(
        gross_amount: Decimal, fee_percent: Decimal, splits: List[Dict]
    ) -> Dict:
        fee_value = SplitService.round(gross_amount * fee_percent / 100, ROUND_HALF_UP)

        net_amount = gross_amount - fee_value

        accumulator = Decimal("0.00")
        receivables = []
        receivables_qnt = len(splits)

        for split in splits:
            recipient_id = split["recipient_id"]
            percent = Decimal(str(split["percent"]))

            recp_amount = SplitService.round(net_amount * percent / 100)
            accumulator += recp_amount

            receivables.append({"recipient_id": recipient_id, "amount": recp_amount, "role": split.get("role", "")})

        leftover = net_amount - accumulator
        if leftover > Decimal("0.00"):
            amount_per_recp = SplitService.round(leftover / receivables_qnt)
            left_accumulator = Decimal("0.00")
            for i, recp in enumerate(receivables):
                is_last = i == receivables_qnt - 1
                if not is_last:
                    recp["amount"] += amount_per_recp
                    left_accumulator += amount_per_recp
                else:
                    recp["amount"] += leftover - left_accumulator

        return {
            "gross_amount": gross_amount,
            "net_amount": net_amount,
            "fee_amount": fee_value,
            "receivables": receivables,
        }

    @staticmethod
    def round(decimal_value: Decimal, rounding=ROUND_DOWN) -> Decimal:
        return decimal_value.quantize(Decimal("0.01"), rounding=rounding)
