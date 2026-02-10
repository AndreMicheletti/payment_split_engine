from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from app.api.serializers import PaymentSerializer

class PaymentsViewSet(viewsets.GenericViewSet):

    @action(detail=False, methods=["post"], serializer_class=PaymentSerializer)
    def payments(self, request):
      serializer = self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)

      data = serializer.validated_data
      return JsonResponse({"message": "Payment processed successfully"}, status=201)
