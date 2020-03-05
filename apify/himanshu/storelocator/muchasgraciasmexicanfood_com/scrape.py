import csv
import requests
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    base_url = "http://muchasgraciasmexicanfood.com"
    r = requests.get(
        "http://muchasgraciasmexicanfood.com/our-locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    address = []
    for city in soup.find_all("ul",{"class":"sub-menu"})[1].find_all("ul",{"class":"sub-menu"}):
        for url in city.find_all("a"):
            page_url = url['href']
            location_r = session.get(page_url, headers=headers)
            location_soup = BeautifulSoup(location_r.text, "lxml")
            location_name = location_soup.find_all("h6",{"class":"avaris-contact-title"})[0].text
            addr = location_soup.find_all("h6",{"class":"avaris-contact-title"})[1].text
            if len(addr.split(",")) == 2:
                street_address = " ".join(addr.split(",")[0].split(" ")[:-1]).replace("Grants","").strip()
                city = addr.split(",")[0].split(" ")[-1].replace("Pass","Grants Pass")
                state = addr.split(",")[1].split(" ")[1]
                zipp = addr.split(",")[1].split(" ")[2]
            else:
                street_address = addr.split(",")[0]
                city = addr.split(",")[1]
                if len(addr.split(",")[-1].split(" ")) == 2:
                    state = addr.split(",")[-1].split(" ")[1]
                    zipp = "<MISSING>"
                else:
                    state = addr.split(",")[-1].split(" ")[1]
                    zipp = addr.split(",")[-1].split(" ")[2]
            phone = location_soup.find_all("h6",{"class":"avaris-contact-title"})[-1].text.strip()
            geo_location = location_soup.find("a", {"href": re.compile("/@")})['href']
            latitude = geo_location.split("/@")[1].split(",")[0]
            longitude = geo_location.split("/@")[1].split(",")[1]
            
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
