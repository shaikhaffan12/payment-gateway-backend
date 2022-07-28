from django.urls import path
from .views import ProductView, checkoutSession, stripe_webhook_view

urlpatterns = [
    path('product/<int:pk>/', ProductView.as_view(), name='products'),
    path('create-checkout-session/<int:pk>/<int:count>', checkoutSession.as_view(), name='checkoutSession'),
    path('webhook', stripe_webhook_view.as_view(), name='stripe_webhook_view' ),
]