from operator import mod
from django.db import models
import uuid

"""website model"""
class Website(models.Model):
    website_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this')
    website_name = models.CharField(max_length=200)
    website_url = models.URLField(max_length=200)



"""product model"""
class Product(models.Model):

    """Model representing a product."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this')
    product_name = models.CharField(max_length=200)
    product_category = models.CharField(max_length=200)
    product_subcategory = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=6, decimal_places=2)
    product_brand = models.CharField(max_length=200)

    class Meta:
        ordering = [ 'product_price', 'product_category','product_name', 'product_subcategory', 'product_brand']
    
    def __str__(self):
        """String for representing the Model object."""
        return self.product_name


"""product website model"""
class ProductWebsite(models.Model):
  
#   //primary key
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this')
  
#   foreign keys
  product = models.ForeignKey(Product, on_delete=models.RESTRICT, null=True)
  website = models.ForeignKey(Website, on_delete=models.RESTRICT, null=True)
 
  shipping_time = models.DateTimeField(null=True, blank=True)
  delivery_charge = models.DecimalField(max_digits=6, decimal_places=2)
  popularity_count = models.IntegerField(default=0)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  available_count = models.IntegerField(default=0)
  image_path = models.CharField(max_length=200)

  class Meta:
    ordering = [ '-price']
  
  def __str__(self):
      return self.product_id.product_name



class Offer(models.Model):

    offer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this')
   
    product_website  = models.ForeignKey(ProductWebsite, on_delete=models.RESTRICT, null=True)
    
    discount_percentage = models.DecimalField(max_digits=3)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_free_shipping = models.BooleanField(default=False)
    buy_one_get_one_free = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['discount_percentage']

    def __str__(self):
        return self.offer_id
        

class Specification(models.Model):

    spec_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this')
   
    spec_name = models.CharField(max_length=200)
    
    
    class Meta:
        ordering = ['spec_name']
    def __str__(self):
        return self.spec_name

class ProductSpecification(models.Model):
     product_website = models.ForeignKey(ProductWebsite, on_delete=models.RESTRICT, null=True, primary_key=True)
     spec = models.ForeignKey(Specification, on_delete=models.RESTRICT, null=True, primary_key=True)

    #  def __str__(self):
    #      return self.spec.spec_name