from django.urls import path
from billing.views.billing import billing_page, generate_bill, previous_bill, bill_detail,mail_sales_bill
from billing.views.product import seed_products
from billing.views.login import login_view, logout_view


urlpatterns = [
    # auth
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # products urls
    path('product/seed/', seed_products, name='seed_products'),

    # Billing Main
    path('billing/', billing_page, name='billing_page'),
    path('generate-bill/', generate_bill, name='generate_bill'),
    path('bill_detail/', bill_detail, name='bill_detail'),
    path('previous_bill/', previous_bill, name='previous_bill'),

    #mail template
    path("bill/<str:purchase_no>/", mail_sales_bill, name="mail_sales_bill"),
]