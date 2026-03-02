from django.db import models

# Create your models here.

class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Product Name')
    desc = models.TextField(null=True, blank=True)
    available_stocks = models.IntegerField(default=0)
    price_per_unit = models.FloatField(default=0.0) # float as mentioned
    tax_percent = models.FloatField(default=0.0) # float as mentioned
    is_active = models.BooleanField(default=True) # for  delete
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'products'


class SalesBill(models.Model):
    customer_email = models.EmailField()
    purchase_date = models.DateTimeField()
    purchase_no = models.CharField(max_length=15, null=True, blank=True)
    total_price_without_tax = models.DecimalField(max_digits=12,decimal_places=2)
    total_tax = models.DecimalField(max_digits=12,decimal_places=2)
    net_price = models.DecimalField(max_digits=12,decimal_places=2)
    rounded_net_price = models.IntegerField()
    cash_received = models.DecimalField(max_digits=12,decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sales_bill'

class SalesBillItem(models.Model):
    sales_bill = models.ForeignKey(SalesBill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price_at_sale = models.DecimalField(max_digits=12,decimal_places=2)
    tax_at_sale = models.DecimalField(max_digits=12,decimal_places=2,help_text="Tax Percent")
    tax_amount = models.DecimalField(max_digits=12,decimal_places=2)
    net_price = models.DecimalField(max_digits=12,decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sales_bill_item'