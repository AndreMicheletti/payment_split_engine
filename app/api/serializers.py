from rest_framework import serializers

from app.models import PaymentMethod


class SplitSerializer(serializers.Serializer):
    recipient_id = serializers.CharField(max_length=255, required=True)
    role = serializers.CharField(max_length=50, required=False, allow_blank=True)
    percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)

    def validate_percent(self, value):
        if value <= 0 or value > 100:
            raise serializers.ValidationError(
                "Percent must be greater than 0 and less than or equal to 100."
            )
        return value


class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=3, required=True)
    payment_method = serializers.ChoiceField(
        choices=PaymentMethod.choices(), required=True
    )
    installments = serializers.IntegerField(min_value=1, required=True)

    splits = SplitSerializer(many=True, required=True)

    def validate_currency(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter ISO code.")
        if value.upper() not in ["BRL"]:
            raise serializers.ValidationError(
                "Unsupported currency. Supported currencies are BRL."
            )
        return value.upper()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_installments(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError(
                "Installments must be at least 1 and at most 12."
            )
        return value

    def validate_payment_method(self, value):
        return value.lower()

    def validate_splits(self, value):
        if len(value) <= 0 or len(value) > 5:
            raise serializers.ValidationError(
                "Splits must contain between 1 and 5 entries."
            )

        total_percent = sum(split["percent"] for split in value)
        if total_percent != 100:
            raise serializers.ValidationError("Total percent of splits must equal 100.")
        return value

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)

        if (
            validated_attrs["payment_method"] == PaymentMethod.PIX
            and validated_attrs["installments"] > 1
        ):
            raise serializers.ValidationError(
                "PIX payment method does not support installments greater than 1."
            )
        return validated_attrs


class ReceivableSerializer(serializers.Serializer):
    recipient_id = serializers.CharField(max_length=255)
    role = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class OutboxEventSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=50)
    status = serializers.CharField(max_length=50)


class PaymentResponseSerializer(serializers.Serializer):
    payment_id = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=50)

    gross_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    platform_fee_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    receivables = ReceivableSerializer(many=True)
    outbox_event = OutboxEventSerializer()
