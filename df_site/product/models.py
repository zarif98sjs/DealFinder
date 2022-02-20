from django.db import models
import uuid

# Create your models here.


class Website(models.Model):
	"""Model representing a website"""
	# primary key
	website_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for website')
	website_name = models.CharField(max_length=200)
	website_url = models.URLField(max_length=200)

	def __str__(self):
		return self.website_name


class Product(models.Model):
	"""Model representing a product"""
	# primary key
	product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for product')

	product_name = models.CharField(max_length=1000)
	product_category = models.CharField(max_length=200)
	product_subcategory = models.CharField(max_length=200)
	product_brand = models.CharField(max_length=200)
	product_buy_count = models.IntegerField(default=0)

	class Meta:
		ordering = ['product_name', 'product_category', 'product_subcategory', 'product_brand']

	def __str__(self):
		"""String for representing the Model object."""
		return self.product_name


class ProductWebsite(models.Model):
	"""Model representing product-website relation"""

	# primary key
	product_website_id = models.UUIDField(
		primary_key=True, default=uuid.uuid4, help_text='Unique ID for product-website relation')

	# foreign keys
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, unique=False)
	website = models.ForeignKey(Website, on_delete=models.CASCADE, null=True, unique=False)

	shipping_time = models.DateTimeField(null=True, blank=True)
	delivery_charge = models.DecimalField(default=0, max_digits=6, decimal_places=2)
	popularity_count = models.IntegerField(default=0)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	available_count = models.IntegerField(default=0)
	image_path = models.CharField(null=True, max_length=200)
	url = models.CharField(null=True, max_length=200)

	class Meta:
		ordering = ['product_website_id']

	def __str__(self):
		return self.product.product_name + ", " + self.website.website_name


class Offer(models.Model):
	"""Model representing offers"""
	# primary key
	offer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for offer')

	# foreign key
	product_website = models.ForeignKey(ProductWebsite, on_delete=models.CASCADE, null=True)

	discount_percentage = models.DecimalField(default=0, max_digits=5, decimal_places=2)
	discount_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	start_date = models.DateTimeField(null=True, blank=True)
	end_date = models.DateTimeField(null=True, blank=True)
	is_free_shipping = models.BooleanField(default=False)
	buy_one_get_one_free = models.BooleanField(default=False)

	def __str__(self):
		return self.offer_id

	def saved_amount(self):
		return self.product_website.price - self.discount_amount


class Specification(models.Model):
	"""Model representing specifications"""
	# primary key
	spec_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for specification')
	spec_name = models.CharField(max_length=1000)

	class Meta:
		ordering = ['spec_name']

	def __str__(self):
		return self.spec_name


class ProductSpecification(models.Model):
	"""Model representing relation between product and specifications"""
	# primary key
	product_spec_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for product specification relation')
	# foreign keys
	product_website = models.ForeignKey(ProductWebsite, unique=False, on_delete=models.CASCADE)
	spec = models.ForeignKey(Specification, unique=False, on_delete=models.CASCADE)
	spec_val = models.CharField(default="", max_length=1000)

	def __str__(self):
		return self.product_website.product.product_name + ": " + self.spec.spec_name