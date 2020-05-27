import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime

def write_output(data):
    with open('data.csv',newline='', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []

    page_url_list =[]
    base_url= "https://www.safeway.com/pharmacy"

    
    headers = {           
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    
    }
    r = requests.get("https://local.safeway.com/index.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    content = soup.find_all("a",{"class":"Directory-listLink"})
    url1 = "https://local.safeway.com/"+content[0]['href']
    r3 = requests.get(url1,headers=headers)
    soup3 = BeautifulSoup(r3.text, "lxml")
    all_link = soup3.find_all("a",{"class":"Directory-listLink"})
    for link in all_link:
        state_link = "https://local.safeway.com/"+link['href']
        r4 = requests.get(state_link, headers=headers)
        soup4 = BeautifulSoup(r4.text, "lxml")
        city_data = soup4.find_all("a",{"class":"Directory-listLink"})
        for i in city_data:
            location_link = i['href'].replace("../safeway/","https://local.pharmacy.safeway.com/")
            # print(location_link)
        
            if "(1)" in i['data-count']:
                page_urls = location_link
                # print(page_urls)
                page_url_list.append(page_urls)
            else:
        
                r6 = requests.get(location_link, headers=headers)
                soup6 = BeautifulSoup(r6.text, "lxml")
                data_link = soup6.find_all("a",{"class":"Teaser-titleLink"})
                for j in data_link:
                    page_urls = j['href'].replace("../","https://local.pharmacy.safeway.com/")
                    # print(page_urls)
                    page_url_list.append(page_urls)
    # print(page_url_list)
    for page_url in page_url_list:
        # print(page_url)
        r5 = requests.get(page_url, headers=headers)
        soup5 = BeautifulSoup(r5.text, "lxml")
        try:
            location_name = soup5.find("h1",{"class":"ContentBanner-h1"}).text
            street_address = soup5.find("span",{"class":"c-address-street-1"}).text
            city = soup5.find("span",{"class":"c-address-city"}).text
            state = soup5.find("abbr",{"class":"c-address-state"}).text
            zipp = soup5.find("span",{"class":"c-address-postal-code"}).text
            phone = soup5.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
            hours = " ".join(list(soup5.find("table",{"class":"c-hours-details"}).stripped_strings)).replace("Day of the Week","").replace("Hours","").strip()
            latitude = soup5.find("meta",{"itemprop":"latitude"})['content']
            longitude = soup5.find("meta",{"itemprop":"longitude"})['content']
            location_type = "Pharmacy"
            country_code = "US"
            
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone )
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            # print("data =="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
        except:
            # print(page_url)
            continue

            













                    # r7 = requests.get(page_url, headers=headers)
                    # soup7 = BeautifulSoup(r7.text, "lxml")
                    # location_name = soup7.find("h1",{"class":"ContentBanner-h1"}).text
                    # street_address = soup7.find("span",{"class":"c-address-street-1"}).text
                    # city = soup7.find("span",{"class":"c-address-city"}).text
                    # state = soup7.find("abbr",{"class":"c-address-state"}).text
                    # zipp = soup7.find("span",{"class":"c-address-postal-code"}).text
                    # phone = soup7.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
                    # hours = soup7.find("table",{"class":"c-hours-details"}).text.replace("Day of the Week","").replace("Hours","")
                    # latitude = soup7.find("meta",{"itemprop":"latitude"})['content']
                    # longitude = soup7.find("meta",{"itemprop":"longitude"})['content']
                    # location_type = "Pharmacy"
                    # country_code = "US"
                    # store = []
                    # store.append(base_url)
                    # store.append(location_name)
                    # store.append(street_address)
                    # store.append(city)
                    # store.append(state)
                    # store.append(zipp)
                    # store.append(country_code)
                    # store.append("<MISSING>")
                    # store.append(phone )
                    # store.append(location_type)
                    # store.append(latitude)
                    # store.append(longitude)
                    # store.append(hours)
                    # store.append(page_url)
                    # # if store[2] in addresses:
                    # #     continue
                    # # addresses.append(store[2])
                    # # print("data =="+str(store))
                    # # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    # yield store

    # url = "https://local.safeway.com/"+content[1]['href']
    # r1 = requests.get(url, headers=headers)
    # soup1 = BeautifulSoup(r1.text, "lxml")
    # list_link = soup1.find_all("a",{"class":"Directory-listLink"})
    # for link in list_link:
    #     location_link = link['href'].replace("..","https://local.pharmacy.safeway.com/")

    #     r2 = requests.get(location_link, headers=headers)
    #     soup2 = BeautifulSoup(r2.text,"lxml")
    #     location_name = soup2.find("h1",{"class":"ContentBanner-h1"}).text
    #     street_address = soup2.find("span",{"class":"c-address-street-1"}).text
    #     city = soup2.find("span",{"class":"c-address-city"}).text
    #     state = soup2.find("abbr",{"class":"c-address-state"}).text
    #     zipp = soup2.find("span",{"class":"c-address-postal-code"}).text
    #     phone = soup2.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
    #     hours = soup2.find("table",{"class":"c-hours-details"}).text.replace("Day of the Week","").replace("Hours","")
    #     latitude = soup2.find("meta",{"itemprop":"latitude"})['content']
    #     longitude = soup2.find("meta",{"itemprop":"longitude"})['content']
    #     page_url = location_link
    #     print(page_url)
    #     location_type = "Pharmacy"
    #     country_code = "US"

    #     store = []
    #     store.append(base_url)
    #     store.append(location_name)
    #     store.append(street_address)
    #     store.append(city)
    #     store.append(state)
    #     store.append(zipp)
    #     store.append(country_code)
    #     store.append("<MISSING>")
    #     store.append(phone )
    #     store.append(location_type)
    #     store.append(latitude)
    #     store.append(longitude)
    #     store.append(hours)
    #     store.append(page_url)
    #     # print("data =="+str(store))
    #     # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    #     yield store
        
       
        
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
