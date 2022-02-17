import json
from bs4 import BeautifulSoup
from requests import session

website_name = "Techland"
baseurl = "https://www.techlandbd.com/"

## Product
class Product:
    def __init__(self,title,url,image_url,regular_price,offer_price,specs,category):
        self.title = title
        self.url = url
        self.image_url = image_url
        self.regular_price = regular_price
        self.specs = specs
        self.brand = ""
        self.offer_price = offer_price
        self.category = category
        self.subcategory = ""

    def setBrand(self,brand):
        self.brand = brand
        
    def __str__(self):
        text = "Title : " + self.title + "\n"
        text += "URL : " + self.url + "\n"
        text += "Image URL : " + self.image_url + "\n"
        text += "Regular Price : " + self.regular_price + "\n"
        text += "Offer Price :" + self.offer_price + "\n"
        text += "Brand : " + self.brand + "\n"
        text += "Category: " + self.category + "\n"
        text += "Sub Category: " + self.subcategory + "\n"
        text += "Specs : \n"
        for spec in self.specs:
            text += spec + "\n"
        text += "\n"
        return text
    
    def get_json(self):
        obj = {
            "Title": self.title,
            "URL": self.url,
            "Image URL": self.image_url,
            "Regular Price": self.regular_price,
            "Offer Price": self.offer_price,
            "Brand": self.brand,
            "Category": self.category,
            "Sub Category": self.subcategory,
            "Specs": self.specs

        }
        return obj

def getBrandInfo(products):
    for p in products:
        r = ses.get(p.url)
        if(r.status_code == 200):
            soup = BeautifulSoup(r.text, 'html.parser')
            brand = soup.find('li',attrs={"class" : "product-manufacturer"}).find('a').text
            p.setBrand(brand)

def getSession():
    with session() as ses:
        r = ses.post(baseurl)
        return ses

def getAllProducts(ses,category):

    products = []

    r = ses.get(baseurl + category)

    for page in range(1,2):
        url = baseurl + category + "?page=" + str(page)
        r = ses.get(url)

        if(r.status_code == 200):
            soup = BeautifulSoup(r.text, 'html.parser')
        
            all_ = soup.find_all('div',class_ ='product-thumb')
            # print(all[0])
            for item in all_:
                temp = item.find('div',{"class":"name"})
                title = temp.find('a').text
                url = temp.find('a').get('href')
                image_url = item.find('div',{"class":"image"}).find('img')['data-src']
                price_new = item.find('div',class_ ='price').find('span',{"class":"price-new"})
                if price_new is not None:
                    offer_price = price_new.text
                    regular_price = item.find('div',class_ ='price').find('span',{"class":"price-old"}).text
                else:
                    regular_price = item.find('div',class_ ='price').find('span',{"class":"price-normal"}).text
                    offer_price = regular_price
                temp_list = item.find('div',class_ ='description').find_all('li')
                specs = []
                for spec in temp_list:
                    specs.append(spec.text)
                products.append(Product(title,url,image_url,regular_price,offer_price,specs,category))

    getBrandInfo(products)
    return products

ses = getSession()

categories = ['brand-laptops', 'desktop-computer', 'pc-components', 'computer-monitor',
              'ups', 'shop-graphics-tablet', 'office-solution', 'shop-cameras', 'security-surveillance',
              'server-networking', 'accessories', 'shop-software', 'tv-home-entertainment',
              'smart-watch-gadget', 'gaming-chair-table']

with open(website_name + ".json", "w", encoding="utf-8") as file:
	data = {"products" : []}
	for category in categories:
		try:
			products = [p.get_json() for p in getAllProducts(ses, category)]
			data["products"] += products
			print(category, "scraped")
			
		except:
			print("Connection problem during", category)
	json.dump(data, file)
	
