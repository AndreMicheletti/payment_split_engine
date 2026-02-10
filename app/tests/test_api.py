from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from uuid import uuid4
from app.models import PaymentModel


class PaymentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_payment_with_pix_and_two_splits(self):
        """
        Ensure we can create a payment with PIX and two splits.
        """
        url = "/v1/payments/"
        data = {
            "amount": "100.00",
            "currency": "BRL",
            "payment_method": "pix",
            "installments": 1,
            "splits": [
                {"recipient_id": "producer_1", "role": "producer", "percent": 50},
                {"recipient_id": "producer_1", "role": "affiliate", "percent": 50},
            ],
        }
        headers = {"Idempotency-Key": uuid4()}
        response = self.client.post(url, data, headers=headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_payment_idempotency(self):
        url = "/v1/payments/"
        data = {
            "amount": "100.00",
            "currency": "BRL",
            "payment_method": "pix",
            "installments": 1,
            "splits": [
                {"recipient_id": "producer_1", "role": "producer", "percent": 50},
                {"recipient_id": "producer_1", "role": "affiliate", "percent": 50},
            ],
        }
        headers = {"Idempotency-Key": uuid4()}
        response = self.client.post(url, data, headers=headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentModel.objects.count(), 1)

        response = self.client.post(url, data, headers=headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PaymentModel.objects.count(), 1)

    def test_payment_idempotency_conflict(self):
        url = "/v1/payments/"
        data = {
            "amount": "100.00",
            "currency": "BRL",
            "payment_method": "pix",
            "installments": 1,
            "splits": [
                {"recipient_id": "producer_1", "role": "producer", "percent": 50},
                {"recipient_id": "producer_1", "role": "affiliate", "percent": 50},
            ],
        }
        headers = {"Idempotency-Key": uuid4()}
        response = self.client.post(url, data, headers=headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentModel.objects.count(), 1)

        # Change payload
        data["amount"] = "200.00"

        response = self.client.post(url, data, headers=headers, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(PaymentModel.objects.count(), 1)
