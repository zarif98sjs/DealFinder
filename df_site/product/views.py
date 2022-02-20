from django.shortcuts import render
import json
import re
from decimal import Decimal
import random

from product.models import Website, Product, ProductWebsite, Offer, Specification, ProductSpecification
import uuid
from datetime import datetime, timedelta

# Create your views here.
loaded = True


# get queryset from product_website ids
def get_query_set(prod_web_ids):
	return ProductWebsite.objects.filter(product_website_id__in=[uuid.UUID(id) for id in prod_web_ids])


# save product_website ids to session
def save_ids_to_session(request, product_list):
	request.session["product_website_ids"] = [str(p.product_website_id) for p in product_list]


# save categories to session 
def save_categories_to_session(request, category_list):
	request.session["categories"] = category_list


# get category list
def get_categories(request):
	if not request.session.has_key("categories"):
		categories_queryset = Product.objects.all().order_by('product_category').values('product_category').distinct()
		categories = [d['product_category'] for d in categories_queryset]
		save_categories_to_session(request, categories)
		return categories
	else:
		return request.session["categories"]


# get specification list from product list
def get_specifications(product_list):
	specification_list = []

	for p in product_list:
		specs = ProductSpecification.objects.filter(product_website=p)
		specification_list.append(list(specs))

	return specification_list


# get offer list from product list
def get_offers(product_list):
	offers = []
	for p in product_list:
		offer = Offer.objects.filter(product_website=p)
		print(len(offer))
		if len(offer) == 0:
			offers.append(None)
		else:
			print("aage", offer[0].product_website)
			offers.append(offer[0])
			print("pore", offer[0].product_website)
	return offers


def get_datalist(product_list):
	offer_list = get_offers(product_list)
	specifications_list = get_specifications(product_list)
	data_list = []
	for i in range(len(product_list)):
		data_list.append({
			"product_website": product_list[i],
			"offer": offer_list[i],
			"specifications": specifications_list[i]
		})
	return data_list


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

					if discount_amount > 0.0:
						if p['Offer Deadline'] == "":
							end_date = datetime.now() + timedelta(days=30)
						else:
							end_date = datetime.strptime(p['Offer Deadline'], "%B %d, %Y %H:%M:%S")
							print(end_date)

						offer = Offer(
							product_website=product_website, discount_amount=discount_amount,
							discount_percentage=(discount_amount / regular_price) * 100,
							end_date=end_date
						)
						offer.save()

					specs = p['Specs']

					if len(specs.keys()) > 0:

						for spec_name in specs.keys():
							existing = Specification.objects.filter(spec_name__contains=spec_name)
							if len(existing) == 0:
								spec_entry = Specification(spec_name=spec_name)
								spec_entry.save()
							else:
								spec_entry = existing[0]

							product_spec = ProductSpecification(product_website=product_website, spec=spec_entry,
							                                    spec_val=specs[spec_name])
							product_spec.save()

		except Exception as e:
			print("Problem in ", website)
			print(e)
			pass

	loaded = True


def home(request):
	load_database()

	# ---------------load category names in categories as list--------------------
	categories = get_categories(request)

	# -------------------------demo list of all---------------------------------------------------
	product_list = list(ProductWebsite.objects.all()[0:100])
	random.shuffle(product_list)
	trending_deals = product_list[0:8]
	editors_pick = product_list[8: 16]
	featured_products = product_list[16:24]
	print(featured_products)
	# ---------------------------remove after updating trending_deals and others------------------

	# top offers by discount amounts
	top_offers = list(Offer.objects.all().order_by("-discount_percentage"))[0:8]
	offer_product_list = [o.product_website for o in top_offers]

	return render(request, 'product/index.html', {
		'categories': categories, 'trending_deals': get_datalist(trending_deals),
		'editors_pick': get_datalist(editors_pick),
		'featured_products': get_datalist(featured_products), 'top_offers': get_datalist(offer_product_list)
	})


def select_category(request, category_name):
	# ---------------------------load category names in categories as list-------------------------
	categories = get_categories(request)

	# get product_list according to category
	product_list = list(ProductWebsite.objects.filter(product__product_category__contains=category_name))
	save_ids_to_session(request, product_list)
	request.session["main_product_website_ids"] = request.session["product_website_ids"]
	data_list = get_datalist(product_list)

	return render(request, 'product/shop.html', {
		'search_key': category_name, 'data_list': data_list, 'categories': categories,
	})


def search(request):

	categories = get_categories(request)
	product_list = []
	# -----------------------------------------------------------------------------------------------
	if request.method == 'POST':
		search_key = request.POST['search_key']
		brand_matches = ProductWebsite.objects.filter(product__product_brand__contains=search_key)
		category_matches = ProductWebsite.objects.filter(product__product_category__contains=search_key)
		subcategory_matches = ProductWebsite.objects.filter(product__product_subcategory__contains=search_key)
		name_matches = ProductWebsite.objects.filter(product__product_name__contains=search_key)
		product_query_set = brand_matches | category_matches | subcategory_matches | name_matches

		product_list = list(product_query_set)
		save_ids_to_session(request, product_list)
		request.session["main_product_website_ids"] = request.session["product_website_ids"]

	data_list = get_datalist(product_list)
	return render(request, 'product/shop.html', {
		'search_key': request.POST['search_key'], 'data_list': data_list, 'categories': categories
	})


def search_name(request, search_key):
	# search inside a product / brand page
	categories = get_categories(request)
	new_product_list = []

	if request.method == 'POST':
		search_name = request.POST['search_name']

		try:
			prod_web_ids = request.session["main_product_website_ids"]
			product_query_set = get_query_set(prod_web_ids)

			name_matches = product_query_set.filter(product__product_name__contains=search_name)
			brand_matches = product_query_set.filter(product__product_brand__contains=search_name)
			category_matches = product_query_set.filter(product__product_category__contains=search_name)

			new_product_queryset = name_matches | brand_matches | category_matches
			new_product_list = list(new_product_queryset)

			save_ids_to_session(request, new_product_list)

		except:
			print("No initial search list found for search name")

	data_list = get_datalist(new_product_list)

	return render(request, 'product/shop.html', {
		'search_key': search_key, 'data_list': data_list, 'categories': categories
	})


def sort(request, search_key, sort_type):

	categories = get_categories(request)
	new_product_list = []
	try:
		prod_web_ids = request.session["product_website_ids"]
		product_query_set = get_query_set(prod_web_ids)

		if sort_type == "Unit Price Low To High":
			new_product_list = list(product_query_set.order_by("price"))
		elif sort_type == "Unit Price High To Low":
			new_product_list = list(product_query_set.order_by("-price"))
		elif sort_type == "Latest":
			offers = Offer.objects.filter(product_website__product_website_id__in=prod_web_ids).order_by("end_date")
			new_product_list = [o.product_website for o in offers]

		save_ids_to_session(request, new_product_list)
	except:
		print("No search list found for sorting")

	data_list = get_datalist(new_product_list)

	return render(request, 'product/shop.html', {
		'search_key': search_key, 'data_list': data_list, 'categories': categories
	})


def filter(request, search_key, filter_type):

	categories = get_categories(request)
	new_product_list = []
	try:
		prod_web_ids = request.session["main_product_website_ids"]
		product_query_set = get_query_set(prod_web_ids)
		new_product_list = list(product_query_set)

		if request.method == 'POST':
			# ----------------------------------Filter by Price----------------------------------------
			if filter_type == 'by_price':
				price_range_selected = request.POST.getlist('price')
				new_product_queryset = ProductWebsite.objects.none()
				for i in range(len(price_range_selected)):
					lower_limit, upper_limit = price_range_selected[i].split("-")
					new_product_queryset |= product_query_set.filter(price__gte=lower_limit).filter(
						price__lte=upper_limit)

				new_product_queryset = new_product_queryset.order_by('price')
				new_product_list = list(new_product_queryset)
			# ----------------------------------Filter by Discount Percentage----------------------------------------
			elif filter_type == "by_discount_perc":
				disc_range_selected = request.POST.getlist('disc_perc')
				offers = Offer.objects.filter(product_website__product_website_id__in=prod_web_ids)
				new_offer_set = Offer.objects.none()
				for i in range(len(disc_range_selected)):
					lower_limit, upper_limit = disc_range_selected[i].split("-")
					new_offer_set |= offers.filter(discount_percentage__gt=lower_limit). \
						filter(discount_percentage__lte=upper_limit)

				new_offer_set = new_offer_set.order_by('-discount_percentage')
				new_product_list = [o.product_website for o in new_offer_set]
			# ----------------------------------Filter by Discount Amount----------------------------------------
			elif filter_type == "by_discount_amt":
				disc_range_selected = request.POST.getlist('disc_amt')
				offers = Offer.objects.filter(product_website__product_website_id__in=prod_web_ids)
				new_offer_set = Offer.objects.none()
				for i in range(len(disc_range_selected)):
					lower_limit, upper_limit = disc_range_selected[i].split("-")
					new_offer_set |= offers.filter(discount_amount__gt=lower_limit). \
						filter(discount_amount__lte=upper_limit)

				new_offer_set = new_offer_set.order_by('-discount_amount')
				new_product_list = [o.product_website for o in new_offer_set]
			# ----------------------------------Other Filters------------------------------------------
			elif filter_type == 'other filters':
				other_filters_selected = request.POST.getlist('others')
				offers = Offer.objects.filter(product_website__product_website_id__in=prod_web_ids)
				if "ending soon" in other_filters_selected:
					offers = offers.order_by("end_date")[:10]

				new_product_list = [o.product_website for o in offers]
			save_ids_to_session(request, new_product_list)

	except:
		print("no list to filter")

	data_list = get_datalist(new_product_list)
	return render(request, 'product/shop.html', {
		'search_key': search_key, 'data_list': data_list, 'categories': categories

	})
