import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://kruseandmuerrestaurants.com"
    r = session.get(
        "https://kruseandmuerrestaurants.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "kruseandmuerrestaurants"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    for val in soup.find_all('li',{"id":"menu-item-49"}):
        for j in val.find_all("li"):
            link = (j.find("a")['href'])
            r_location = session.get(link, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")
            location_name = soup_location.find('div',{"class":"fl-rich-text"})
            data = (list(location_name.stripped_strings))
            street_address = data[0]
            try:
                city = data[1].split(",")[0]
                state = data[1].split(",")[1].strip().split( )[0]
                zipp =data[1].split(",")[1].strip().split( )[1]
            except:
                city = data[1].split(" ")[0]
                state = data[1].split(" ")[1]
                zipp =data[1].split(" ")[2]
            phone  = data[-1]
            location_name = soup_location.find('h2',{"class":"fl-heading"}).text.strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "Kruse and Muer Restaurants"
            hours = (soup_location.find('tbody',{"class":"uabb-table-features"}))
            hours_of_operation = (" ".join(list(hours.stripped_strings)))
            if "https://kruseandmuerrestaurants.com/location/kabin-krusers-oyster-bar/" in link:
                latitude = "42.771463"
                longitude = "-83.243752"
            if "48346" in zipp:
                latitude = soup_location.find('a',{"class":"map-btn"})['href'].split("/@")[1].split(",")[0]
                longitude = soup_location.find('a',{"class":"map-btn"})['href'].split("/@")[1].split(",")[1]
            elif "Kruse's Paint Creek Tavern" in location_name:
                latitude = soup_location.find_all('address',{"class":"lead"})[-1].find("a")['href'].split("/@")[1].split(",")[0]
                longitude = soup_location.find_all('address',{"class":"lead"})[-1].find("a")['href'].split("/@")[1].split(",")[1]
            elif "in the village rochester hills" in location_name or "Rochester chop house" in location_name or "roadhouse lake orion" in location_name :
                latitude = soup_location.find('a',{"class":"map-btn"})['href'].split("ll=")[1].split(",")[0]
                longitude = soup_location.find('a',{"class":"map-btn"})['href'].split("ll=")[1].split("&s")[0].split(",")[1]
            elif "Kruse and muer on main" in location_name :
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            elif "48067" in zipp :
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation,link]
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
