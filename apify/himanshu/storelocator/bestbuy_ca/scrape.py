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
    base_url= "https://stores.bestbuy.ca/en-ca/index.html"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= soup.find_all("li",{"class":"Directory-listItem"})
    
    for i in k:
        link = i.find("a")['data-count'].replace("(",'')
        if link != "1)":
            city_link = "https://stores.bestbuy.ca"+i.find("a")['href'].replace("..","")
            # print(city_link)
    
            r1 = requests.get(city_link)
            soup1= BeautifulSoup(r1.text,"lxml")
            citylink= soup1.find_all("li",{"class":"Directory-listItem"})
            
            for c in citylink:
                link1 = c.find("a")['data-count'].replace("(",'')
                if link1 != "1)":
                    sublink = "https://stores.bestbuy.ca"+c.find("a")['href'].replace("..","")
                    r2 = requests.get(sublink)
                    soup2= BeautifulSoup(r2.text,"lxml")
                    store_link = soup2.find_all("a",class_="Teaser-titleLink")
                 
                    for st in store_link:
                        # print("https://stores.bestbuy.ca"+st['href'].replace("../..",""))
                        r3 = requests.get("https://stores.bestbuy.ca"+st['href'].replace("../..",""))
                        page_url ="https://stores.bestbuy.ca"+st['href'].replace("../..","")
                        soup3= BeautifulSoup(r3.text,"lxml")

                        streetAddress = soup3.find("span",{"class":"c-address-street-1"}).text.strip()
                        state = soup3.find("abbr",{"itemprop":"addressRegion"}).text
                        zip1 = soup3.find("span",{"itemprop":"postalCode"}).text
                        city = soup3.find("span",{"class":"c-address-city"}).text
                        name = " ".join(list(soup3.find("h1",{"itemprop":"name"}).stripped_strings))
                        phone = soup3.find("span",{"itemprop":"telephone"}).text
                        hours = " ".join(list(soup3.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup3.find("meta",{"itemprop":"latitude"})['content']
                        longitude = soup3.find("meta",{"itemprop":"longitude"})['content']
                        
                        tem_var =[]
                        tem_var.append("https://www.bestbuy.ca/")
                        tem_var.append(name)
                        tem_var.append(streetAddress)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("CA")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("<MISSING>")
                        tem_var.append(latitude)
                        tem_var.append(longitude)
                        tem_var.append(hours)
                        tem_var.append(page_url)
                        yield tem_var
                        # print("========================================",tem_var)

                else:
                    # print(c.find("a")['href'])
                    # print(c.find("a")['href'])
                    # print("https://stores.bestbuy.ca"+c.find("a")['href'].replace("..",""))
                    # print('-------------------------')
                    one_link="https://stores.bestbuy.ca"+c.find("a")['href'].replace("..","")
                    page_url = one_link
                    r4 = requests.get(one_link)
                    soup4= BeautifulSoup(r4.text,"lxml")

                    streetAddress = soup4.find("span",{"class":"c-address-street-1"}).text.strip()
                    state = soup4.find("abbr",{"itemprop":"addressRegion"}).text
                    zip1 = soup4.find("span",{"itemprop":"postalCode"}).text
                    city = soup4.find("span",{"class":"c-address-city"}).text
                    name = " ".join(list(soup4.find("h1",{"itemprop":"name"}).stripped_strings))
                    phone = soup4.find("span",{"itemprop":"telephone"}).text
                    hours = " ".join(list(soup4.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
                  
                    latitude = soup4.find("meta",{"itemprop":"latitude"})['content']
                    longitude = soup4.find("meta",{"itemprop":"longitude"})['content']

                    tem_var =[]
                    tem_var.append("https://www.bestbuy.ca/en-ca")
                    tem_var.append(name)
                    tem_var.append(streetAddress)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("CA")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    tem_var.append(page_url)
                    yield tem_var
                    # print("========================================",tem_var)
        else:
            # print("--------------------------------------------",link)
            # print(i.find("a")['href'].replace("..",""))
            # print("https://stores.bestbuy.ca"+i.find("a")['href'].replace("..",""))
            one_link1 = "https://stores.bestbuy.ca"+i.find("a")['href'].replace("..","")
            page_url = one_link1
            r5 = requests.get(one_link1)
            soup5= BeautifulSoup(r5.text,"lxml")
            streetAddress = soup5.find("span",{"class":"c-address-street-1"}).text.strip()
            # streetAddress = soup5.find("span",{"itemprop":"streetAddress"}).text.strip()


            streetAddress = soup5.find("span",{"class":"c-address-street-1"}).text.strip()
            state = soup5.find("abbr",{"itemprop":"addressRegion"}).text
            zip1 = soup5.find("span",{"itemprop":"postalCode"}).text
            city = soup5.find("span",{"class":"c-address-city"}).text
            name = " ".join(list(soup5.find("h1",{"itemprop":"name"}).stripped_strings))
            phone = soup5.find("span",{"itemprop":"telephone"}).text
            hours = " ".join(list(soup5.find("table",{"class":"c-location-hours-details"}).find("tbody").stripped_strings))
            latitude = soup5.find("meta",{"itemprop":"latitude"})['content']
            longitude = soup5.find("meta",{"itemprop":"longitude"})['content']
        
            tem_var =[]
            tem_var.append("https://www.bestbuy.ca/en-ca")
            tem_var.append(name)
            tem_var.append(streetAddress)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("CA")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours)
            tem_var.append(page_url)
            yield tem_var
            # print("========================================",tem_var)
         


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


