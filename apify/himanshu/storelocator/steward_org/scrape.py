import csv
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import json
import phonenumbers
session = SgRequests()
def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    base_url="https://www.steward.org/"
    locator_domain = base_url
    r= session.get("https://locations.steward.org/?_ga=2.114374343.1517144285.1587465653-1472301885.1587465653",headers= headers)
    soup = BeautifulSoup(r.text,"lxml")
    state_list = soup.find("div",class_="state-list-column").find("div",class_="c-directory-list")
    for link in state_list.find_all("a",class_="c-directory-list-content-item-link"):
        a = "https://locations.steward.org/"+link["href"]
        # print(a)
        r1 = session.get(a,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        try:
            for city_link in soup1.find("ul",class_="c-directory-list-content").find_all("li",class_="c-directory-list-content-item"):
                a1 = "https://locations.steward.org/"+city_link.find("a",class_="c-directory-list-content-item-link")["href"]
                r2 = session.get(a1,headers=headers)
                soup2 = BeautifulSoup(r2.text,"lxml")
                for location in soup2.find_all("div",class_="c-location-grid-col"):
                    location_name = location.find("span",class_="location-name-brand").text.strip()
                    page_url = "https://locations.steward.org"+location.find("h1",class_="c-location-grid-item-title").find("a")["href"].replace("..","").strip()
                    street_address = location.find("span",class_="c-address-street").text.split("Suite")[0].split("Ste")[0].split(",")[0].strip()
                    if "Floor" in street_address:
                        street_address =  " ".join(street_address.split()[:-2])
                    street_address = street_address.split("\n")[0].strip()
                    city = location.find("span",class_="c-address-city").text.replace(",","").strip()
                    state = location.find("abbr",class_="c-address-state").text.strip()
                    zipp = location.find("span",class_="c-address-postal-code").text.strip()
                    country_code = "US"
                    store_number = "<MISSING>"
                    phone = location.find("span",class_="c-phone-number-span c-phone-main-number-span").text.strip()
                    location_type = "<MISSING>"
                    
                    r3 = session.get(page_url,headers = headers)
                    soup3 = BeautifulSoup(r3.text,"lxml")
                    try:
                        hours_of_operation = " ".join(list(soup3.find("table",class_="c-location-hours-details").stripped_strings)).replace("Day of the Week Hours","").strip()
                    except:
                        # print("page_url == ",page_url)
                        hours_of_operation = "<MISSING>"
                    latitude = soup3.find("meta",{"itemprop":"latitude"})["content"]
                    longitude   = soup3.find("meta",{"itemprop":"longitude"})["content"]
                    # print(city)
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    store = [x if x else "<MISSING>" for x in store]

                    if (store[1]+" "+store[2]+" "+store[-3]) in addresses:
                        continue
                    addresses.append(store[1]+" "+store[2]+" "+store[-3])
                    #print("data = " + str(store))
                    #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
                    

        except:
            loc_grid = soup1.find("div",class_="c-location-grid")
            if loc_grid != None:
                for location in loc_grid.find_all("div",class_="c-location-grid-col"):
                    location_name = location.find("span",class_="location-name-brand").text.strip()
                    page_url = "https://locations.steward.org"+location.find("h1",class_="c-location-grid-item-title").find("a")["href"].replace("..","").strip()
                    street_address = location.find("span",class_="c-address-street").text.split("Suite")[0].split("Ste")[0].split(",")[0].strip()
                    if "Floor" in street_address:
                        street_address =  " ".join(street_address.split()[:-2])
                   
                    street_address = street_address.split("\n")[0].strip()
                    city = location.find("span",class_="c-address-city").text.replace(",","").strip()
                    state = location.find("abbr",class_="c-address-state").text.strip()
                    zipp = location.find("span",class_="c-address-postal-code").text.strip()
                    country_code = "US"
                    store_number = "<MISSING>"
                    phone = location.find("span",class_="c-phone-number-span c-phone-main-number-span").text.strip()
                    location_type = "<MISSING>"
                    r3 = session.get(page_url,headers = headers)
                    soup3 = BeautifulSoup(r3.text,"lxml")
                    try:
                        hours_of_operation = " ".join(list(soup3.find("table",class_="c-location-hours-details").stripped_strings)).replace("Day of the Week Hours","").strip()
                    except:
                        # print("page_url == ",page_url)
                        hours_of_operation = "<MISSING>"
                    latitude = soup3.find("meta",{"itemprop":"latitude"})["content"]
                    longitude   = soup3.find("meta",{"itemprop":"longitude"})["content"]
                    # print(city)
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    store = [x if x else "<MISSING>" for x in store]

                    if (store[1]+" "+store[2]+" "+store[-3]) in addresses:
                        continue
                    addresses.append(store[1]+" "+store[2]+" "+store[-3])

                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
            else:
                page_url = a
                location_name = "<MISSING>"
                street_address = list(soup1.find("a",{"itemprop":"address"}).stripped_strings)[0]
                city = list(soup1.find("a",{"itemprop":"address"}).stripped_strings)[-1].split()[0]
                state = list(soup1.find("a",{"itemprop":"address"}).stripped_strings)[-1].split()[1]
                zipp = list(soup1.find("a",{"itemprop":"address"}).stripped_strings)[-1].split()[-1]
                country_code = "US"
                phone = soup1.find("span",{"itemprop":"telephone"}).text
                hours_of_operation = " ".join(list(soup1.find("table",class_="c-location-hours-details").stripped_strings)).replace("Day of the Week Hours","").strip()
                location_type = "<MISSING>"
                store_number = "<MISSING>"
                latitude = soup1.find("meta",{"itemprop":"latitude"})["content"]
                longitude   = soup1.find("meta",{"itemprop":"longitude"})["content"]
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [x if x else "<MISSING>" for x in store]

                if (store[1]+" "+store[2]+" "+store[-3]) in addresses:
                        continue
                addresses.append(store[1]+" "+store[2]+" "+store[-3])
                # print(street_address)
                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
                
    r = session.get("https://www.steward.org/network/our-hospitals",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for data in soup.find_all("div",{"col-md-4 col-sm-6 col-xs-12 state-location"}):
        location_name = data.find("h3").text
        addr = list(data.find("div",{"class":"state-location-left"}).find("div").stripped_strings)
        street_address = addr[1]
        city = addr[-1].split(",")[0]
        state = addr[-1].split(",")[-1].split()[0]
        zipp = addr[-1].split(",")[-1].split()[1]
        phone = phonenumbers.format_number(phonenumbers.parse(str(data.find("a",{"class":"phone"})['href'].replace("tel:","")), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        page_url = data.find("a",{"class":"website"})['href']
        store =[]
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("HOSPITAL")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        if (store[1]+" "+store[2]) in addresses:
            continue
        addresses.append(store[1]+" "+store[2])

        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

        yield store
    
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
