from django.shortcuts import render,redirect, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from billing.forms import LookupEmailForm
from billing.models import Product, SalesBillItem, SalesBill
from django.db.models import Prefetch
from billing.utils import send_email
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import F
from django.utils import timezone
from django.db import transaction
from billing.utils import get_denominations
from django.conf import settings

import json
from datetime import datetime
from decimal import Decimal
import logging
logger = logging.getLogger(__name__)
# Create your views here.


DENOMINATIONS = [500,50,20,10,5,2,1]


@login_required
@api_view(('GET',))
def billing_page(request):
    """
    # API - Billing Screen
    # URL - /billing/
    
    """
    try:
        products = Product.objects.filter(is_active=True)

        return render(request, 'billing.html', {'products': products,'denominations':DENOMINATIONS})
    
    except Exception as e:
        logger.exception("Exception {}".format(e.args))
        raise


@login_required
@api_view(['POST'])
def generate_bill(request):
    """
    URL - /generate-bill/
    """
    try:
        data = request.data
        customer_email = data.get("customer_email")
        items = data.get("items", [])
        cash_paid = Decimal(str(data.get("cash_paid", 0)))

        if not customer_email:
            return Response({"status": 'fail', "message": "invalid Customer email"}, status=400)

        if not items:
            return Response({"status": 'fail', "message": "select prodycts"}, status=400)

        total_without_tax = Decimal("0.00")
        total_tax = Decimal("0.00")
        response_items = []

        with transaction.atomic():
            for item in items:
                product_id = item.get("product")
                quantity = int(item.get("quantity", 0))
                if quantity <= 0:
                    return Response({"status": 'fail', "message": "Invalid quantity"}, status=400)

                product = Product.objects.select_for_update().get(product_id=product_id)
                if product.available_stocks < quantity:
                    return Response({"status": 'fail',"message": f"Insufficient stock for {product.name}"}, status=400)

                unit_price = Decimal(str(product.price_per_unit))
                tax_percent = Decimal(str(product.tax_percent))

                tax_rate = tax_percent / Decimal(100)
                base_price_per_unit = unit_price / (Decimal(1) + tax_rate)
                tax_per_unit = unit_price - base_price_per_unit
                purchase_price = base_price_per_unit * quantity
                tax_amount = tax_per_unit * quantity
                line_total = unit_price * quantity

                total_without_tax += purchase_price
                total_tax += tax_amount

                product.available_stocks = F('available_stocks') - quantity
                product.save(update_fields=['available_stocks'])

                response_items.append({
                    "product_id": product.product_id,
                    "product_name": product.name,
                    "unit_price": unit_price,
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "tax_percentage": tax_percent,
                    "tax_amount": tax_amount,
                    "total_price": line_total,
                })
            net_price = total_without_tax + total_tax
            rounded_net_price = net_price.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            balance = cash_paid - rounded_net_price
            if balance < 0:
                return Response({"status": 'fail',"message": "Insufficient cash "}, status=400)

            bill = SalesBill.objects.create(
                customer_email=customer_email,
                purchase_date=timezone.now(),
                purchase_no=f"INV{timezone.now().strftime('%Y%m%d%H%M%S')}",
                total_price_without_tax=total_without_tax,
                total_tax=total_tax,
                net_price=net_price,
                rounded_net_price=int(rounded_net_price),
                cash_received=cash_paid )

            for r_item in response_items:
                SalesBillItem.objects.create(
                    sales_bill=bill,
                    product=Product.objects.get(product_id=r_item["product_id"]),
                    quantity=r_item["quantity"],
                    unit_price_at_sale=r_item["unit_price"],
                    tax_at_sale=r_item["tax_percentage"],
                    tax_amount=r_item["tax_amount"],
                    net_price=r_item["total_price"])

        # mail send
        link = f"{settings.BASE_URL}/bill/{bill.purchase_no}/"
        mail_dt = {
            'subject': "Recent Purchase Invoice",
            'message': 'Please find you Invoice here.\n {}'.format(link),
            'recipient_list': [customer_email]
        }
        print('-->', mail_dt)
        send_email(**mail_dt)

        balance_denominations = get_denominations(int(balance))

        res_dt = {"purchase_id": bill.id,"customer_email": bill.customer_email,"items": response_items,
            "total_without_tax": total_without_tax,"total_tax": total_tax,"net_price": net_price,"net_price_rounded": rounded_net_price,
            "balance": balance,"balance_denominations": balance_denominations}
        
        # return redirect('bill_detail', res_dt)
        request.session['balance_denominations'] = balance_denominations
        # request.session['balance'] = balance

        return Response({"status": "success","purchase_id": bill.id,"customer_email": bill.customer_email,"items": response_items,
            "total_without_tax": total_without_tax,"total_tax": total_tax,"net_price": net_price,"net_price_rounded": rounded_net_price,
            "balance": balance,"balance_denominations": balance_denominations})

    except Product.DoesNotExist:
        return Response({"status": "fail", "message": "Invalid product"}, status=400)

    except Exception as e:
        logger.exception("Exception {}".format(e.args))
        return Response({"status": 'fail', "message": "somethigns went wrong"},status=400)
    

@login_required
@api_view(['GET'])
def bill_detail(request):
    try:
        bill_id = request.GET.get('bill_id')
        if not bill_id:
            return Response({'status':'fail','message':'Invalid Bill'},status=400)
        
        
        bill = get_object_or_404(SalesBill, id=bill_id)
        items = bill.items.filter(is_active=1)
        balance = Decimal(str(bill.cash_received)) - Decimal(str(bill.rounded_net_price))
        balance_denominations = request.session.pop('balance_denominations', {})

        return render(request, "bill_detail.html", {"bill": bill,"items": items,"balance": balance,"balance_denominations": balance_denominations})

    except Exception as e:
        logger.exception("Exception {}".format(e.args))
        return Response({"status": 'fail', "message": "somethigns went wrong"},status=400)


@login_required
@api_view(['GET'])
def previous_bill(request):
    try:
        form = LookupEmailForm(request.GET or None)
        purchases = None
        email = ''

        if form.is_valid():
            email = form.cleaned_data['email']
            purchases = SalesBill.objects.filter(customer_email=email).prefetch_related('items')

        return render(request, 'previous_bill.html', {'form': form,'purchases': purchases,'email': email})
    
    except Exception as e:
        logger.exception("Exception {}".format(e.args))
        return Response({"status": 'fail', "message": "somethigns went wrong"},status=400)


@api_view(['GET'])
def mail_sales_bill(request, purchase_no):
    try:
        bill = get_object_or_404(SalesBill.objects.prefetch_related('items__product'),purchase_no=purchase_no,is_active=True)
        context = {"bill": bill,"items": bill.items.filter(is_active=True)}
        return render(request, "mail_bill.html", context)

    except Exception as e:
        logger.exception("Exception {}".format(e.args))
        return Response({"status": 'fail', "message": "somethigns went wrong"},status=400)