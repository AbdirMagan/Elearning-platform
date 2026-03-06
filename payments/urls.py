from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:course_slug>/', views.checkout, name='checkout'),
    path('initiate/<slug:course_slug>/', views.initiate_payment, name='initiate_payment'),
    path('status/<uuid:transaction_id>/', views.payment_status, name='payment_status'),
    # path('callback/', views.waafipay_callback, name='waafipay_callback'),
    path('history/', views.transaction_history, name='transaction_history'),
    path('refund/<uuid:transaction_id>/', views.request_refund, name='request_refund'),
]
