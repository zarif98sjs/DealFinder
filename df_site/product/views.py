from django.shortcuts import render
import json
import re
from decimal import Decimal
from product.models import Website, Product, ProductWebsite, Offer, Specification, ProductSpecification

# Create your views here.
loaded = False


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
			with open("../scraper/" + website.website_name + ".json") as file:
				products = json.load(file)['products']
				for p in products:
					regular_price = Decimal(re.sub("[^0-9.]", "", p['Regular Price']))
					discount_amount = regular_price - Decimal(re.sub("[^0-9.]", "", p['Offer Price']))

					product = Product(
						product_name=p['Title'], product_category=p['Category'],
						product_subcategory=p['Sub Category'], product_brand=p['Brand']
					)
					product.save()

					product_website = ProductWebsite(
						product=product, website=website, image_path=p['Image URL'],
						price=regular_price
					)
					product_website.save()

					offer = Offer(
						product_website=product_website, discount_amount=discount_amount,
						discount_percentage=(discount_amount / regular_price) * 100
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
	categories = ['category1', 'category2', 'category3', 'category4', 'category5']
	# also need to send the top products,  trending deals etc
	trending_deals = ['product1', 'product2', 'product3', 'product4', 'product5', 'product6']
	editors_pick = ['product1', 'product2', 'product3', 'product4', 'product5', 'product6']
	featured_products = ['product1', 'product2', 'product3', 'product4', 'product5', 'product6']
	top_offers = ['product1', 'product2', 'product3', 'product4', 'product5', 'product6']
	return render(request, 'product/index.html', {
		'categories': categories, 'trending_deals': trending_deals, 'editors_pick': editors_pick,
		'featured_products': featured_products, 'top_offers': top_offers
	})


def select_category(request, category_name):
	print(category_name)
	# get product_list according to category
	product_list = []
	return render(request, 'product/shop.html', {'search_key': category_name, 'product_list': product_list})


def search(request):
	# after entering something in the search bar of home page
	# pass Model product object list
	# Reference : https://stackoverflow.com/questions/16829764/how-to-pass-an-object-to-html-in-django-view-py
	# -------------------------------------Dummy Product List-----------------------------------------------
	title = "1stPlayer FK 300W Power Supply"
	url = "https://www.startech.com.bd/toshiba-dt01aba100v-1tb-surveillance-hdd"
	image_url = "https://www.startech.com.bd/image/cache/catalog/power-supply/1stplayer/fk-300w/fk-300w-01-228x228.jpg"
	price = 2200
	# specs = [Modular: Non-Modular,  Input Frequency: 50-60Hz
	#                 Input Current: Current 8/10A MAX
	#                 Fan Size120MM Hydraulic Bearing
	#                 Certifications: None 80+]
	# The plan is to show the specs details when clicked in view details
	specs = ""
	brand = "Thermaltake"
	product_list = [
		[title, url, image_url, price, specs, brand],
		[title, url, image_url, price, specs, brand],
		[title, url, image_url, price, specs, brand],
		[title, url, image_url, price, specs, brand],
		[title, url, image_url, price, specs, brand],
	]
	# -------------------------------------Dummy Product List-----------------------------------------------
	if request.method == 'POST':
		print(request.POST['search_key'])
	# check if search_key is a brand name or product name
	# if brand : make product list accordingly
	# if product : make product list accordingly

	return render(request, 'product/shop.html',{
		'search_key': request.POST['search_key'], 'product_list': product_list
	})


def search_name(request, search_key):
	# search inside a product / brand page
	# print(product_list)
	if request.method == 'POST':
		print(request.POST['search_name'])
	# check if search_name is a brand name or product name
	# if brand : make product list accordingly
	# if product : make product list accordingly

	product_list = []
	return render(request, 'product/shop.html', {'search_key': search_key, 'product_list': product_list})


def sort(request, search_key, sort_type):
	print(sort_type)
	# sort accordingly
	# access the product list from session ??
	# Reference : https://stackoverflow.com/questions/9024160/django-pass-object-from-view-to-next-for-processing
	product_list = []
	return render(request, 'product/shop.html', {'search_key': search_key, 'product_list': product_list})

###################################################################################################################
# Naeem - To do list
# Product details pop up - with specs
# Product details show from model object - Stack overflow reference in search function
# Filter implementation - same as sort
# Remove Unnecessary things from homepage and other pages
# Follow Mock UI design
###################################################################################################################
