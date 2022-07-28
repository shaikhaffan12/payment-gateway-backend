from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from .serializer import productSerializer
from .models import product
from rest_framework.response import Response
import stripe
from django.conf import settings
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
# Create your views here.

class ProductView(RetrieveAPIView):
    queryset = product.objects.all()
    serializer_class = productSerializer

    def get(self,request, pk):
        products = product.objects.get(id=pk)
        serializer = self.get_serializer(products)
        return Response(serializer.data)
        
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
class checkoutSession(APIView):
    def post(self, request, *args,**kwargs):
        print(self.kwargs)
        product_id = self.kwargs['pk']
        count = self.kwargs['count']
        try:
            products = product.objects.get(id = product_id)
            checkout_session = stripe.checkout.Session.create(
                line_items = [
                    {
                        'price_data' : {
                            'currency': 'usd',
                            'unit_amount' : products.price * 100,
                            'product_data': {
                                'name' : products.name,
                            }
                        },
                        'quantity': count
                    },
                ],
                mode = 'payment',
                metadata = {
                    'product_id' : products.id,
                },
                success_url = settings.SITE_URL + '?success=true',
                cancel_url = settings.SITE_URL + '?cancel=true',
            )
            return redirect(checkout_session.url, code=303)

        except Exception as  e:
            return Response({'msg':'something went wrong while creating stripe session', 'error': str(e)}, status=500)


class stripe_webhook_view(CreateAPIView):
    def post (request):
        payload = request.body

        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
            payload, sig_header, settings.ENDPOINT_SECRET_KEY
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
        # For now, you only need to print out the webhook payload so you can see
        # the structure.
        print(session)

        return HttpResponse(status=200)