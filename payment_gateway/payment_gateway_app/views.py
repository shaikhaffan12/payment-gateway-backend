from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from .serializer import productSerializer, PaymentDetailSerializer
from .models import product
from rest_framework.response import Response
import stripe
import os
from django.http import HttpResponse
# Create your views here.

# Stripe Secret Key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') 

Site_url = os.environ.get('SITE_URL')
class ProductView(RetrieveAPIView): # view for product
    queryset = product.objects.all()
    serializer_class = productSerializer

    def get(self,request, pk):
        products = product.objects.get(id=pk)
        serializer = self.get_serializer(products)
        return Response(serializer.data)
        


class checkoutSession(APIView): # view for checkout session
    def post(self, request, *args,**kwargs):
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
                                'images':[products.image_url],
                            }
                        },
                        'quantity': count
                    },
                ],
                mode = 'payment',
                metadata = {
                    'product_id' : products.id,
                },
                success_url = Site_url + '?success=true',
                cancel_url = Site_url + '?cancel=true',
            )
            return redirect(checkout_session.url, code=303)

        except Exception as  e:
            return Response({'msg':'something went wrong while creating stripe session', 'error': str(e)}, status=500)


# Stripe webhook view 
class stripe_webhook_view(CreateAPIView):
    serializer_class = PaymentDetailSerializer

    def stripe_webhook(self,session):
        # trace and store data which stripe webhook forward to this end point
        # traced data store in DB 
        slice_data = session["charges"]["data"][0]
        data = {
            "name" : slice_data["billing_details"]["name"],
            "email" : slice_data["billing_details"]["email"],
            "amount" : (slice_data["amount"])/100,
            "city" : slice_data["billing_details"]["address"]["city"],
            "state" : slice_data["billing_details"]["address"]["state"],
            "country" : slice_data["billing_details"]["address"]["country"],
            "status" : slice_data["status"]
        }
        return data

    def post (self,request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        try:
            event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('ENDPOINT_SECRET_KEY')
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        #  it saves failed and succeeded data in DB
        if event['type'] in ['payment_intent.succeeded','payment_intent.payment_failed']:
            session = event['data']['object']
            data = self.stripe_webhook(session)
            serializer = self.get_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        return HttpResponse(status=200)

        