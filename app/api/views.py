import app.models
from django.http import JsonResponse
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action

from app.models import PaymentModel, PaymentStatus, EventType, EventStatus
from app.api.serializers import PaymentSerializer, PaymentResponseSerializer
from app.services.split_service import SplitService

class PaymentsViewSet(viewsets.GenericViewSet):

    @action(detail=False, methods=["post"], serializer_class=PaymentSerializer)
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
