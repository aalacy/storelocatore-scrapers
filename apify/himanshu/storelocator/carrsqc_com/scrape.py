import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('carrsqc_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
    }
    base_url = "https://www.carrsqc.com/"
    r = session.get("https://local.carrsqc.com/index.html")
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find_all("a",{"class":"Directory-listLink"}):
        state_link = "https://local.carrsqc.com/"+link['href']
        city_r = session.get(state_link)
        city_soup = BeautifulSoup(city_r.text, "lxml")
        for url in city_soup.find_all("a",{'class':"Directory-listLink"}):
            if url['data-count'] == (1):
                page_url = "https://local.carrsqc.com/"+url['href']
                location_r = session.get(page_url)
                location_soup = BeautifulSoup(location_r.text, "lxml")
    
                location_name = location_soup.find("h1",{"class":"ContentBanner-h1"}).text
                street_address = location_soup.find("span",{"class":"c-address-street-1"}).text
                city = location_soup.find("span",{"class":"c-address-city"}).text
                state = location_soup.find("abbr",{"class":"c-address-state"}).text
                zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text
                phone = location_soup.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
                hours = location_soup.find("table",{"class":"c-hours-details"}).text.replace("Day of the Week","").replace("Hours","")
                latitude = location_soup.find("meta",{"itemprop":"latitude"})['content']
                longitude = location_soup.find("meta",{"itemprop":"longitude"})['content']
                location_type = "Carrs"
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
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours)
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # logger.info("data======="+str(store))
                yield store
            else:
                r1 = session.get("https://local.carrsqc.com/"+url['href'])
                soup1 = BeautifulSoup(r1.text, "lxml")
                for link in soup1.find_all("a",{"class":"Teaser-titleLink"}):
                    page_url = 'https://local.carrsqc.com/'+link['href'].replace("../",'')
                    location_r = session.get(page_url)
                    location_soup = BeautifulSoup(location_r.text, "lxml")
                    location_name = location_soup.find("h1",{"class":"ContentBanner-h1"}).text
                    street_address = location_soup.find("span",{"class":"c-address-street-1"}).text
                    city = location_soup.find("span",{"class":"c-address-city"}).text
                    state = location_soup.find("abbr",{"class":"c-address-state"}).text
                    zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text
                    phone = location_soup.find("div",{"class":"Phone-display Phone-display--withLink"}).text.strip()
                    hours = location_soup.find("table",{"class":"c-hours-details"}).text.replace("Day of the Week","").replace("Hours","")
                    latitude = location_soup.find("meta",{"itemprop":"latitude"})['content']
                    longitude = location_soup.find("meta",{"itemprop":"longitude"})['content']
                    location_type = "Carrs"
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
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours)
                    store.append(page_url)
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    # logger.info("data======="+str(store))
                    yield store

    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
