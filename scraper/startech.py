import sys

from bs4 import BeautifulSoup
from numpy import unicode
from requests import session

baseurl = "https://www.startech.com.bd/"

## Laptop
class Laptop:
    def __init__(self,title,url,image_url,price,specs):
        self.title = title
        self.url = url
        self.image_url = image_url
        self.price = price
        self.specs = specs
        
    def __str__(self):
        text = "Title : "+self.title+"\n"
        text += "URL : "+self.url+"\n"
        text += "Image URL : "+self.image_url+"\n"
        text += "Price : "+self.price+"\n"
        text += "Specs : \n"
        for spec in self.specs:
            text += spec+"\n"
        text += "\n"
        return text


def getSession():
    with session() as ses:
        r = ses.post(baseurl)
        return ses


def getLaptops(ses):

    laptops = []

    for page in range(1,15):
        r = ses.get(baseurl + 'laptop-notebook' + "?page="+str(page))

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

                laptops.append(Laptop(title,url,image_url,price,specs))
            
    return laptops

ses = getSession()
laptops = getLaptops(ses)
print(len(laptops))
print(laptops[0])