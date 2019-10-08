import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://stores.petco.com"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    addresss =[]
    link= (soup.find_all("a",{"class":"gaq-link","data-gaq":"List, Region"}))
 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    for index,i in enumerate(link):
        # print(i['href'])
        try:
            r = requests.get(i['href'])
            soup1= BeautifulSoup(r.text,"lxml")
        except:
            continue
        link1= soup1.find_all("a",{"class":"gaq-link","data-gaq":"List, City"})

        for j in link1:
            tem_var=[]
            r = requests.get(j['href'],headers=headers)
            soup2= BeautifulSoup(r.text,"lxml")
            details = (soup2.find("a",{"class":"btn btn-primary store-info gaq-link"})['href'])
            r = requests.get(details,headers=headers)
            soup3= BeautifulSoup(r.text,"lxml")
            json1 = json.loads(soup3.find("script",{"type":"application/ld+json"}).text)
            
            # print("============================link",details)
            if "openingHours" in json1[0]:
                hours = json1[0]['openingHours']
            else:
                hours = "<MISSING>"
            latitude = json1[0]['geo']['latitude']
            longitude = json1[0]['geo']['longitude']
            name = json1[0]['mainEntityOfPage']['breadcrumb']['itemListElement'][0]['item']['name']
            # print(json1[0]['address'])
            phone = json1[0]['address']['telephone']
            st = json1[0]['address']['streetAddress']
            city =  json1[0]['address']['addressLocality']
            state = json1[0]['address']['addressRegion']
            zip1 = json1[0]['address']['postalCode']
           
            tem_var.append("https://stores.petco.com")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours)
            tem_var.append(details)
            if tem_var[2] in addresss:
                continue
            addresss.append(tem_var[2])

            # print("===============",tem_var)
            yield tem_var
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


