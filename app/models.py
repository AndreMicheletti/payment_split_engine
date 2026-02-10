from enum import StrEnum
from django.db import models
import uuid


class EventType(StrEnum):
    PAYMENT_CAPTURED = "payment_captured"
    PAYMENT_RECEIVED = "payment_received"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class EventStatus(StrEnum):
    PENDING = "pending"
    PUBLISHED = "published"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PaymentStatus(StrEnum):
    CAPTURED = "captured"
    PROCESSED = "processed"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PaymentMethod(StrEnum):
    PIX = "pix"
    CARD = "card"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PaymentModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices(),
        default=PaymentStatus.CAPTURED,
        null=False,
        blank=False,
    )

    gross_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )

    net_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )

    payment_method = models.CharField(
        max_length=25, choices=PaymentMethod.choices(), null=False, blank=False
    )
    installments = models.PositiveIntegerField(default=1, null=False, blank=False)

    idempotency_key = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, null=False, blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<Payment {self.pk}: {self.status}>"


class LedgerEntryModel(models.Model):
    payment = models.ForeignKey(
        PaymentModel, on_delete=models.CASCADE, related_name="ledger_entries"
    )

    recipient_id = models.CharField(max_length=255, null=False, blank=False)

    role = models.CharField(max_length=50, null=False, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<LedgerEntry {self.payment.pk} - {self.recipient_id}>"


class OutboxEventModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices(),
        default=EventStatus.PENDING,
        null=False,
        blank=False,
    )
    type = models.CharField(
        max_length=50, choices=EventType.choices(), null=False, blank=False
    )

    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"<OutboxEvent {self.pk} - {self.type} ({self.status})>"
