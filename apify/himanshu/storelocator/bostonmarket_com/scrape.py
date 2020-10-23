import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bostonmarket_com')



session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.bostonmarket.com/"

    r_state = requests.get("https://www.bostonmarket.com/location/")
    soup_state = BeautifulSoup(r_state.text, "lxml")

    for state_link in soup_state.find_all("a",{"class":"Directory-listLink"}):
        s_link = state_link['href']
        if state_link['data-count'] == "(1)":
            page_url = "https://www.bostonmarket.com/location/"+s_link
            logger.info(page_url)
            location_r = requests.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")

            location_name = "Boston Market" +" "+location_soup.find("div",{"class":"Core-location"}).text.strip()
            if "Ramstein, Miesenbach" in location_name:
                continue
            street_address = location_soup.find("meta",{"itemprop":"streetAddress"})['content']
            city = location_soup.find("span",{"class":"c-address-city"}).text.strip()
            try:
                state = location_soup.find("abbr",{"itemprop":"addressRegion"}).text.strip()
            except:
                state = "<MISSING>"
            if '689 N Terminal Road' in street_address:
                state='PR'
            zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text.strip()
            try:
                phone = location_soup.find("div",{"itemprop":"telephone"}).text
            except:
                phone = "<MISSING>"
            latitude = location_soup.find("meta", {"itemprop":"latitude"})['content']
            longitude = location_soup.find("meta", {"itemprop":"longitude"})['content']
            store_number = location_soup.find("div",{"class":"Core-id"}).text.split("#")[-1].strip()
            try:
                hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).find("tbody").stripped_strings)).strip()
            except:
                hours = "<MISSING>"

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp )
            store.append("US" if zipp.replace("-","").isdigit() else "CA")
            store.append(store_number)
            store.append(phone)
            store.append("Restaurant")
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            # logger.info("data ==="+str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
            yield store
        else:
            city_link = "https://www.bostonmarket.com/location/"+state_link['href']
            city_r = requests.get(city_link)
            city_soup = BeautifulSoup(city_r.text, "lxml")

            for location in city_soup.find_all("a",{"class":"Directory-listLink"}):
                if location['data-count'] == "(1)":
                    
                    page_url = "https://www.bostonmarket.com/location/"+location['href']
                    # logger.info(page_url)
                    location_r = requests.get(page_url)
                    location_soup = BeautifulSoup(location_r.text, "lxml")
                    location_name = "Boston Market" +" "+location_soup.find("div",{"class":"Core-location"}).text.strip()
                    if "Ramstein, Miesenbach" in location_name:
                        continue
                    street_address = location_soup.find("meta",{"itemprop":"streetAddress"})['content']
                    city = location_soup.find("span",{"class":"c-address-city"}).text.strip()
                    state = location_soup.find("abbr",{"itemprop":"addressRegion"}).text.strip()
                    zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text.strip()
                    try:
                        phone = location_soup.find("div",{"itemprop":"telephone"}).text
                    except:
                        phone = "<MISSING>"
                    latitude = location_soup.find("meta", {"itemprop":"latitude"})['content']
                    longitude = location_soup.find("meta", {"itemprop":"longitude"})['content']
                    store_number = location_soup.find("div",{"class":"Core-id"}).text.split("#")[-1].strip()
                    try:
                        hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).find("tbody").stripped_strings)).strip()
                    except:
                        hours = "<MISSING>"

                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp )
                    store.append("US" if zipp.replace("-","").isdigit() else "CA")
                    store.append(store_number)
                    store.append(phone)
                    store.append("Restaurant")
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours)
                    store.append(page_url)
                    # logger.info("data ==="+str(store))
                    # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
                    yield store

                    
                else:
                    store_link = "https://www.bostonmarket.com/location/"+location['href']
                    store_r = requests.get(store_link)
                    store_soup = BeautifulSoup(store_r.text, "lxml")

                    for location in store_soup.find_all("a",{"class":"Teaser-titleLink"}):
                        page_url = location['href'].replace("..","https://www.bostonmarket.com/location")
                        location_r = requests.get(page_url)
                        location_soup = BeautifulSoup(location_r.text, "lxml")
        
                        # logger.info(page_url)
                        location_name = "Boston Market" +" "+location_soup.find("div",{"class":"Core-location"}).text.strip()
                        if "Ramstein, Miesenbach" in location_name:
                            continue
                        street_address = location_soup.find("meta",{"itemprop":"streetAddress"})['content']
                        city = location_soup.find("span",{"class":"c-address-city"}).text.strip()
                        state = location_soup.find("abbr",{"itemprop":"addressRegion"}).text.strip()
                        zipp = location_soup.find("span",{"class":"c-address-postal-code"}).text.strip()
                        try:
                            phone = location_soup.find("div",{"itemprop":"telephone"}).text
                        except:
                            phone = "<MISSING>"
                        latitude = location_soup.find("meta", {"itemprop":"latitude"})['content']
                        longitude = location_soup.find("meta", {"itemprop":"longitude"})['content']
                        store_number = location_soup.find("div",{"class":"Core-id"}).text.split("#")[-1].strip()
                        try:
                            hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).find("tbody").stripped_strings)).strip()
                        except:
                            hours = "<MISSING>"
                        


                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zipp )
                        store.append("US" if zipp.replace("-","").isdigit() else "CA")
                        store.append(store_number)
                        store.append(phone)
                        store.append("Restaurant")
                        store.append(latitude)
                        store.append(longitude)
                        store.append(hours)
                        store.append(page_url)
                        # logger.info("data ==="+str(store))
                        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
                        yield store



   
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
