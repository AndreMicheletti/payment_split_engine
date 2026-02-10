from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class PaymentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_payment_with_pix_and_two_splits(self):
        """
        Ensure we can create a payment with PIX and two splits.
        """
        url = '/v1/payments/'
        data = {
            "amount": "100.00",
            "currency": "BRL",
            "payment_method": "pix",
            "installments": 1,
            "splits": [
                { "recipient_id": "producer_1", "role": "producer", "percent": 50 },
                { "recipient_id": "producer_1", "role": "affiliate", "percent": 50 }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

