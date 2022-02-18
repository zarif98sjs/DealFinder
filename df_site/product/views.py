from django.shortcuts import render
import json
import re
from decimal import Decimal

from numpy import save
from product.models import Website, Product, ProductWebsite, Offer, Specification, ProductSpecification
import uuid
from django.utils.dateparse import parse_datetime

# Create your views here.
loaded = False
category_saved = False


# get queryset from product_website ids
def get_query_set(prod_web_ids):
	return ProductWebsite.objects.filter(product_website_id__in=[uuid.UUID(id) for id in prod_web_ids])


# save product_website ids to session
def save_ids_to_session(request, product_list):
	request.session["product_website_ids"] = [str(p.product_website_id) for p in product_list]
	print("Saved to session ")
	print(request.session["product_website_ids"])

# save categories to session 
def save_categories_to_session(request, category_list):
	request.session["categories"] = category_list
	print("Saved to session")
	print(request.session["categories"])
	global category_saved
	category_saved = True

# get category list
def get_categories(request):
	if category_saved == False:
		qset = Product.objects.all().order_by('product_category').values('product_category').distinct()
		categories = [d['product_category'] for d in qset]
		save_categories_to_session(request, categories)
		return categories
	else:
		return request.session["categories"]

# insert to database from json files
def load_database():
	global loaded
	if loaded:
		return

	Product.objects.all().delete()
	ProductWebsite.objects.all().delete()
	Specification.objects.all().delete()
	ProductSpecification.objects.all().delete()
	Offer.objects.all().delete()

	websites = Website.objects.all()

	for website in websites:
		try:
			with open("../" + website.website_name + ".json") as file:
				products = json.load(file)['products']
				for p in products:
					try:
						regular_price = Decimal(re.sub("[^0-9.]", "", p['Regular Price']))
					except:
						continue
					try:
						discount_amount = regular_price - Decimal(re.sub("[^0-9.]", "", p['Offer Price']))
					except:
						discount_amount = 0.0

					product = Product(
						product_name=p['Title'], product_category=p['Category'],
						product_brand=p['Brand']
					)
					product.save()

					product_website = ProductWebsite(
						product=product, website=website, image_path=p['Image URL'],
						price=regular_price, url=p['URL']
					)
					product_website.save()

					if p['Offer Deadline'] is None:
						end_date = None
					else:
						end_date = parse_datetime(p['Offer Deadline'])

					offer = Offer(
						product_website=product_website, discount_amount=discount_amount,
						discount_percentage=(discount_amount / regular_price) * 100,
						end_date=end_date
					)
					offer.save()

				# for s in p['Specs']:
				#     specification = Specification(spec_name=s)
				#     specification.save()
				#     print("spec saved")
				#     product_specification = ProductSpecification(
				#         product_website=product_website, specification=specification
				#     )
				#     product_specification.save()
				#     print("prod spec saved")

		except Exception as e:
			print("Problem in ", website)
			print(e)
			pass
	loaded = True


def home(request):

	load_database()

	# homepage load
	# ---------------load category names in categories as list--------------------
	qset = Product.objects.all().order_by('product_category').values('product_category').distinct()
	categories = [d['product_category'] for d in qset]
	print(categories)

	#-------------------------demo list of all---------------------------------------------------
	product_list = list(ProductWebsite.objects.filter(product__product_category__contains="laptop"))
	trending_deals = product_list[0:6]
	editors_pick = product_list[0:6]
	featured_products = product_list[0:6]
	print(featured_products)
	#---------------------------remove after updating trending_deals and others------------------

	# # also need to send the top products,  trending deals etc
	# trending_deals = ['product1', 'product2', 'product3', 'product4', 'product5', 'product6']
	# editors_pick = ['product1', 'product2', 'product3', 'product4', 'product5', 'product6']
	# featured_products = ['product1', 'product2', 'product3', 'product4', 'product5', 'product6']

	

	# top offers by discount amounts
	top_offers = list(Offer.objects.all().order_by("-discount_percentage"))

	return render(request, 'product/index.html', {
		'categories': categories, 'trending_deals': trending_deals, 'editors_pick': editors_pick,
		'featured_products': featured_products, 'top_offers': top_offers
	})


def select_category(request, category_name):
	# ---------------------------load category names in categories as list-------------------------
	categories = get_categories(request)
	#-----------------------------------------------------------------------------------------------
	print("selected category", category_name)
	# get product_list according to category
	product_list = list(ProductWebsite.objects.filter(product__product_category__contains=category_name))
	save_ids_to_session(request, product_list)
	print(product_list)
	return render(request, 'product/shop.html', {
		'search_key': category_name, 'product_list': product_list, 'categories' : categories, 
		})


def search(request):
	# after entering something in the search bar of home page
	# pass Model product object list
	# Reference : https://stackoverflow.com/questions/16829764/how-to-pass-an-object-to-html-in-django-view-py
	# ---------------------------load category names in categories as list-------------------------
	categories = get_categories(request)
	#-----------------------------------------------------------------------------------------------
	if request.method == 'POST':
		search_key = request.POST['search_key']
		print(search_key)
		brand_matches = ProductWebsite.objects.filter(product__product_brand__contains=search_key)
		category_matches = ProductWebsite.objects.filter(product__product_category__contains=search_key)
		subcategory_matches = ProductWebsite.objects.filter(product__product_subcategory__contains=search_key)
		name_matches = ProductWebsite.objects.filter(product__product_name__contains=search_key)
		product_query_set = brand_matches | category_matches | subcategory_matches | name_matches

		product_list = list(product_query_set)
		save_ids_to_session(request, product_list)



	return render(request, 'product/shop.html', {
		'search_key': request.POST['search_key'], 'product_list': product_list, 'categories' : categories
	})


def search_name(request, search_key):
	# search inside a product / brand page
	# print(product_list)
	# ---------------------------load category names in categories as list-------------------------
	categories = get_categories(request)
	#-----------------------------------------------------------------------------------------------

	new_product_list = []

	if request.method == 'POST':
		search_name = request.POST['search_name']
		print(search_name)


		try:
			prod_web_ids = request.session["product_website_ids"]
			product_query_set = get_query_set(prod_web_ids)

			name_matches = product_query_set.filter(product__product_name__contains=search_name)
			brand_matches = product_query_set.filter(product__product_brand__contains=search_name)
			category_matches = product_query_set.filter(product__product_category__contains=search_name)

			new_product_queryset = name_matches | brand_matches | category_matches
			new_product_list = list(new_product_queryset)

			save_ids_to_session(request, new_product_list)

		except:
			print("No initial search list found for search name")


	# check if search_name is a brand name or product name
	# if brand : make product list accordingly
	# if product : make product list accordingly

	return render(request, 'product/shop.html', {
		'search_key': search_key, 'product_list': new_product_list, 'categories' : categories
		})


def sort(request, search_key, sort_type):
	# ---------------------------load category names in categories as list-------------------------
	categories = get_categories(request)
	#-----------------------------------------------------------------------------------------------
	print(sort_type)
	if request.session.has_key("product_website_ids"):
		print("Has saved\n")

	# sort types:
	# 1. Unit Price
	# 2. Latest
	new_product_list = []
	try:
		prod_web_ids = request.session["product_website_ids"]
		print(prod_web_ids)
		product_query_set = get_query_set(prod_web_ids)

		if sort_type == "Unit Price":
			new_product_queryset = product_query_set.order_by("price")
		# elif sort_type == "Latest":
		# 	offers = Offer.objects.filter(product_website__product_website_id__in=prod_web_ids)
		# 	offer = offers.order_by("end")

		new_product_list = list(new_product_queryset)
		save_ids_to_session(request, new_product_list)

	except:
		print("No search list found for sorting")

	# sort accordingly
	# access the product list from session ??
	# Reference : https://stackoverflow.com/questions/9024160/django-pass-object-from-view-to-next-for-processing

	return render(request, 'product/shop.html', {
		'search_key': search_key, 'product_list': new_product_list, 'categories' : categories
		})


def filter(request, search_key, filter_type):
	# ---------------------------load category names in categories as list-------------------------
	categories = get_categories(request)
	#-----------------------------------------------------------------------------------------------
	print(filter_type)
	# sort types:
	# 1. price
	new_product_list = []
	try:
		prod_web_ids = request.session["product_website_ids"]
		product_query_set = get_query_set(prod_web_ids)
		new_product_queryset = product_query_set.order_by("price")

		new_product_list = list(new_product_queryset)
		save_ids_to_session(request, new_product_list)

	except:
		print("No search list found for filtering")

	return render(request, 'product/shop.html', {
		'search_key': search_key, 'product_list': new_product_list, 'categories' : categories
		})

###################################################################################################################
# Naeem - To do list
# Product details pop up - with specs
# Product details show from model object - Stack overflow reference in search function
# Filter implementation - same as sort
# Remove Unnecessary things from homepage and other pages
# Follow Mock UI design
###################################################################################################################
