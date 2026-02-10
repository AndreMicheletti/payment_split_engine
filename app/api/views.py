import functools
import hashlib
import json
from django.http import JsonResponse
from django.db import transaction
from rest_framework import viewsets, serializers
from rest_framework.decorators import action

from app.models import PaymentModel, PaymentStatus, EventType, EventStatus, LedgerEntryModel
from app.api.serializers import PaymentSerializer, PaymentResponseSerializer
from app.services.split_service import SplitService

IDEMPOTENCY_CACHE = {}
RESPONSE_CACHE = {}

def idempotency_decorator(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            raise serializers.ValidationError("Idempotency-Key header is required.")

        canonical_data = json.dumps(request.data, sort_keys=True, separators=(",", ":"))
        hash_object = hashlib.sha256(canonical_data.encode('utf-8'))
        payload_hash = hash_object.hexdigest()
        
        if idempotency_key in IDEMPOTENCY_CACHE:
            if payload_hash != IDEMPOTENCY_CACHE[idempotency_key]:
                return JsonResponse({"message": "Duplicity detected."}, status=409)
            else:
                return JsonResponse(RESPONSE_CACHE[idempotency_key], status=200)

        response = func(self, request, *args, **kwargs)

        IDEMPOTENCY_CACHE[idempotency_key] = payload_hash
        RESPONSE_CACHE[idempotency_key] = json.loads(response.content)

        return response
    return wrapper

class PaymentsViewSet(viewsets.GenericViewSet):

    @action(detail=False, methods=["post"], serializer_class=PaymentSerializer)
    @idempotency_decorator
    def payments(self, request):
        idempotency_key = request.headers.get("Idempotency-Key")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        platform_fee = SplitService.calculate_fee(
            payment_method=data["payment_method"],
            installments=data["installments"],
        )

        calculated_data = SplitService.calculate(
            gross_amount=data["amount"],
            fee_percent=platform_fee,
            splits=data["splits"],
        )
        
        with transaction.atomic():
            payment = PaymentModel.objects.create(
                status=PaymentStatus.CAPTURED,
                gross_amount=calculated_data["gross_amount"],
                fee_amount=calculated_data["fee_amount"],
                net_amount=calculated_data["net_amount"],
                payment_method=data["payment_method"],
                installments=data["installments"],
                idempotency_key=idempotency_key,
            )
            
            LedgerEntryModel.objects.bulk_create(
                [
                    LedgerEntryModel(
                        payment=payment,
                        recipient_id=recp["recipient_id"],
                        role="payee",
                        amount=recp["amount"],
                    )
                    for recp in calculated_data["receivables"]
                ]
            )

        response_data = {
            "payment_id": str(payment.id),
            "status": payment.status,
            "gross_amount": payment.gross_amount,
            "platform_fee_amount": payment.fee_amount,
            "net_amount": payment.net_amount,
            "receivables": calculated_data["receivables"],
            "outbox_event": {
            "type": EventType.PAYMENT_RECEIVED,
            "status": EventStatus.PENDING,
            },
        }
        response_serializer = PaymentResponseSerializer(response_data)

        return JsonResponse(response_serializer.data, status=201)
