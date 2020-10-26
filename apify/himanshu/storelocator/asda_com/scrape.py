import json
import urllib.parse
import time
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

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
    base_url= "https://storelocator.asda.com/directory"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= soup.find_all("li",{"class":"Directory-listItem"})
    for i in k:
        link = i.find("a")['data-count'].split("(")[-1]
        if link != "1)":
            city_link = "https://storelocator.asda.com/"+i.find("a")['href']
            try:
                r1 = session.get(city_link)
            except:
                pass
            soup1= BeautifulSoup(r1.text,"lxml")
            citylink= soup1.find_all("li",{"class":"Directory-listItem"})
            for c in citylink:
                link1 = c.find("a")['data-count'].split("(")[-1]
                if link1 != "1)":
                    sublink = "https://storelocator.asda.com/"+c.find("a")['href']
                    r2 = session.get(sublink)
                    soup2= BeautifulSoup(r2.text,"lxml")
                    store_link = soup2.find_all("a",class_="Teaser-titleLink")
                    for st in store_link:
                        r3 = session.get("https://storelocator.asda.com"+st['href'].replace("..",""))
                        page_url = "https://storelocator.asda.com"+st['href'].replace("..","")
                        soup3= BeautifulSoup(r3.text,"lxml")
                        streetAddress = soup3.find("meta",{"itemprop":"streetAddress"})['content']
                        # state = soup3.find("abbr",{"class":"c-address-state"}).text
                        state = "<MISSING>"
                        zip1 = soup3.find("span",{"class":"c-address-postal-code"}).text
                        city = soup3.find("span",{"class":"c-address-city"}).text
                        name = " ".join(list(soup3.find("h1",{"class":"Core-title"}).stripped_strings))
                        phone = soup3.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                        hours = " ".join(list(soup3.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                        latitude = soup3.find("meta",{"itemprop":"latitude"})['content']
                        longitude = soup3.find("meta",{"itemprop":"longitude"})['content']
                        
                        tem_var =[]
                        tem_var.append("https://www.asda.com")
                        tem_var.append(name)
                        tem_var.append(streetAddress)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zip1)
                        tem_var.append("UK")
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
                    one_link="https://storelocator.asda.com/"+c.find("a")['href']
                    page_url = one_link
                    r4 = session.get(one_link)
                    soup4= BeautifulSoup(r4.text,"lxml")

                    streetAddress = soup4.find("meta",{"itemprop":"streetAddress"})['content']
                    # state = soup3.find("abbr",{"class":"c-address-state"}).text
                    state = "<MISSING>"
                    zip1 = soup4.find("span",{"class":"c-address-postal-code"}).text
                    city = soup4.find("span",{"class":"c-address-city"}).text
                    name = " ".join(list(soup4.find("h1",{"class":"Core-title"}).stripped_strings))
                    phone = soup4.find("div",{"class":"Phone-display Phone-display--withLink"}).text
                    hours = " ".join(list(soup4.find("table",{"class":"c-hours-details"}).find("tbody").stripped_strings))
                    latitude = soup4.find("meta",{"itemprop":"latitude"})['content']
                    longitude = soup4.find("meta",{"itemprop":"longitude"})['content']
                

                    tem_var =[]
                    tem_var.append("https://www.asda.com")
                    tem_var.append(name)
                    tem_var.append(streetAddress)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zip1)
                    tem_var.append("UK")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(latitude)
                    tem_var.append(longitude)
                    tem_var.append(hours)
                    tem_var.append(page_url)
                    yield tem_var

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


