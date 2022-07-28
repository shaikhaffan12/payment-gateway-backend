from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from .serializer import productSerializer
from .models import product, payment_detail
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

def stripe_webhook(session):
    customer_name = session["charges"]["data"][0]["billing_details"]["name"]
    customer_email = session["charges"]["data"][0]["billing_details"]["email"]
    order_total = session["charges"]["data"][0]["amount"]
    user_city = session["charges"]["data"][0]["billing_details"]["address"]["city"]
    user_state = session["charges"]["data"][0]["billing_details"]["address"]["state"]
    user_country = session["charges"]["data"][0]["billing_details"]["address"]["country"]
    payment_status = session["charges"]["data"][0]["status"]

    str_amt = str(order_total)
    paid_amount = str_amt[:-2]
    payment_detail.objects.create(name=customer_name, email=customer_email, amount=paid_amount, city= user_city, state = user_state, country = user_country, status = payment_status)
    

class stripe_webhook_view(CreateAPIView):
    def post (self,request):
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
        if event['type'] == 'payment_intent.succeeded':
            session = event['data']['object']
        # For now, you only need to print out the webhook payload so you can see
        # the structure.
            stripe_webhook(session)

        return HttpResponse(status=200)

        