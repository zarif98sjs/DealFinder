import sys

from bs4 import BeautifulSoup
from requests import session

baseurl = "https://www.startech.com.bd/"

## Product
class Product:
    def __init__(self,title,url,image_url,price,specs):
        self.title = title
        self.url = url
        self.image_url = image_url
        self.price = price
        self.specs = specs
        self.brand = ""

    def setBrand(self,brand):
        self.brand = brand
        
    def __str__(self):
        text = "Title : "+self.title+"\n"
        text += "URL : "+self.url+"\n"
        text += "Image URL : "+self.image_url+"\n"
        text += "Price : "+self.price+"\n"
        text += "Brand : "+self.brand+"\n"
        text += "Specs : \n"
        for spec in self.specs:
            text += spec+"\n"
        text += "\n"
        return text

class SubCategory:
    def __init__(self,title,url):
        self.title = title
        self.url = url

    def __str__(self):
        text = "Title : "+self.title+"\n"
        text += "URL : "+self.url+"\n"
        return text

def getSession():
    with session() as ses:
        r = ses.post(baseurl)
        return ses

def getSubCategories(ses,category):

    sub_categories = []

    r = ses.get(baseurl + category)

    if(r.status_code == 200):
        soup = BeautifulSoup(r.text, 'html.parser')
        all_ = soup.find('div',class_ ='child-list').find_all('a')
        for sub_c in all_:
            title = sub_c.contents[0]
            link = sub_c.get('href')
            sub_categories.append(SubCategory(title,link))

    return sub_categories

def getBrandInfo(products):

    for p in products:

        r = ses.get(p.url)

        if(r.status_code == 200):
            soup = BeautifulSoup(r.text, 'html.parser')
            all_ = soup.find('tr',attrs={"class" : "product-info-group","itemprop":"brand"})
            brand = all_.find('td',attrs={"class" : "product-info-data product-brand"}).contents[0]
            p.setBrand(brand)


def getAllProducts(ses,category):

    products = []

    r = ses.get(baseurl + category)

    for page in range(1,2):
        r = ses.get(baseurl + category + "?page="+str(page))

        if(r.status_code == 200):
            soup = BeautifulSoup(r.text, 'html.parser')
        
            all_ = soup.find_all('div',class_ ='p-item')

            for item in all_:
                temp = item.find('h4',class_ ='p-item-name').find('a')
                title = temp.contents[0]
                url = temp.get('href')
                image_url = item.find('div',class_ ='p-item-img').find('a').find('img')['src']
                price = item.find('div',class_ ='p-item-price').find('span').contents[0]
                temp_list = item.find('div',class_ ='short-description').find('ul').find_all('li')

                specs = []
                for spec in temp_list:
                    specs.append(spec.text)

                products.append(Product(title,url,image_url,price,specs))

    getBrandInfo(products)

    return products

ses = getSession()

categories = ['laptop-notebook','desktops', 'component', 'monitor', 'ups-ips', 'tablet-pc', 'office-equipment', 'camera', 'Security-Camera', 'networking', 'accessories', 'software', 'server-networking', 'television-shop', 'gadget', 'gaming']

# sub_categories = getSubCategories(ses,categories[2])

products  = getAllProducts(ses,categories[2])

# print(len(products))
# print(len(sub_categories))
# print("----------------------")
# print("Sub Categories :")
# for s_c in sub_categories:
#     print(s_c)
# print("Demo Product :")
# print(products[1])
# print("---")
# print(products[2])
# print("---")
print(products[10])
