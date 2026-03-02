from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from billing.models import Product


@api_view(('GET',))
def seed_products( request):
    """
    # API - Seed Sample data to Database
    # URL - http://localhost:8000/product/seed

    # Sample Response
        {
            "status": "success",
            "message": "Products seeded successfully"
        }
    """
    try:
        mock_dt = [
            { "name": "Dove", "desc": "Dove Soap 50 Gm", "available_stocks":10, "price_per_unit": 50, "tax_percent": 5 },
            { "name": "Mysore Sandal", "desc": "Mysore Soap 70 Gm", "available_stocks":10, "price_per_unit": 60, "tax_percent": 5 },
            { "name": "Pears", "desc": "Pears Soap 30 Gm", "available_stocks":10, "price_per_unit": 40, "tax_percent": 0 },
            { "name": "Medimix", "desc": "Medimix Soap 50 Gm", "available_stocks":10, "price_per_unit": 30, "tax_percent": 5 },
            { "name": "Cinthol", "desc": "Cinthol Soap 50 Gm", "available_stocks":10, "price_per_unit": 35, "tax_percent": 12 },
            { "name": "Lifebuoy", "desc": "Lifebuoy Soap 20 Gm", "available_stocks":10, "price_per_unit": 10, "tax_percent": 5 },
            { "name": "Hamam", "desc": "Hamam Soap 70 Gm", "available_stocks":10, "price_per_unit": 55, "tax_percent": 18 },
            { "name": "Chandrika", "desc": "Chandrika Soap 60 Gm", "available_stocks":10, "price_per_unit": 70, "tax_percent": 0 }
        ]
        product_list = []
        for i in mock_dt:
            product_list.append(Product(**i))

        Product.objects.bulk_create(product_list)

        return Response({'status':'success','message':'Products seeded successfully'})
        

    except Exception as e:
        return Response({'status':'fail', 'message':'Somethings went wrong'}, status=500)

