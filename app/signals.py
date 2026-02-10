from django.dispatch import Signal, receiver

from app.models import EventType, OutboxEventModel

payment_received = Signal()


@receiver(payment_received)
def create_outbox_event(sender, payment, receivables, **kwargs):
    OutboxEventModel.objects.create(
        type=EventType.PAYMENT_RECEIVED,
        payload={
            "payment_id": str(payment.id),
            "status": payment.status,
            "gross_amount": str(payment.gross_amount),
            "fee_amount": str(payment.fee_amount),
            "net_amount": str(payment.net_amount),
            "payment_method": payment.payment_method,
            "installments": payment.installments,
            "receivables": [
                {
                    **recp,
                    "amount": str(recp["amount"]),
                }
                for recp in receivables
            ],
        },
    )
