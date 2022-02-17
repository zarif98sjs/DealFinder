import sys

from bs4 import BeautifulSoup
from requests import session

baseurl = "https://www.techlandbd.com/"

def getSession():
    with session() as ses:
        r = ses.post(baseurl)
        return ses

## Product
class Product:
    def __init__(self,title,url,image_url,regular_price,offer_price,specs):
        self.title = title
        self.url = url
        self.image_url = image_url
        self.regular_price = regular_price
        self.specs = specs
        self.brand = ""
        self.offer_price = offer_price

    def setBrand(self,brand):
        self.brand = brand
        
    def __str__(self):
        text = "Title : "+self.title+"\n"
        text += "URL : "+self.url+"\n"
        text += "Image URL : "+self.image_url+"\n"
        text += "Regular Price : "+self.regular_price+"\n"
        text += "Offer Price : "+self.offer_price+"\n"
        text += "Brand : "+self.brand+"\n"
        text += "Specs : \n"
        for spec in self.specs:
            text += spec+"\n"
        text += "\n"
        return text

def getBrandInfo(products):
    for p in products:
        r = ses.get(p.url)
        if(r.status_code == 200):
            soup = BeautifulSoup(r.text, 'html.parser')
            brand = soup.find('li',attrs={"class" : "product-manufacturer"}).find('a').text
            p.setBrand(brand)

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
                products.append(Product(title,url,image_url,regular_price,offer_price,specs))

    getBrandInfo(products)
    return products

ses = getSession()
products = getAllProducts(ses,"brand-laptops")
print(products[0])