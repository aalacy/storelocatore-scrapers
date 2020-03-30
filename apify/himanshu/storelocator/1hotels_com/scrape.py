import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.1hotels.com"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("ul", {"class": "menu menu-level-0"}):
            semi_part = parts.find_all("li", {"class": "menu-item menu-item--expanded"})[0]
            for inner_semi_part in semi_part.find_all("span", {"class": "menu-item col-12 col-md-4 col-lg-3","data-id":"open-2"}):
                if (inner_semi_part.find("a")):
                    page_url = base_url + inner_semi_part.find("a")['href']
                    store_request = session.get(page_url,headers=headers)
                    store_soup = BeautifulSoup(store_request.text, "lxml")
                    phone_request = session.get(base_url + store_soup.find("a",text=re.compile("Contact Us"))["href"],headers=headers)
                    phone_soup = BeautifulSoup(phone_request.text, "lxml")
                    phone = ""
                    for a in phone_soup.find_all("a",{"href":re.compile("tel: ")}):
                        if a.findPrevious("strong"):
                            if "Hotel" in a.findPrevious("strong").text:
                                phone = a.text.strip()
                    if phone == "":
                        phone = phone_soup.find("a",{"href":re.compile("tel: ")}).text.strip()
                    temp_iframe = store_soup.find("p",{"class": "directions__address"})
                    find_url = temp_iframe.find("a")['href']
                    geo_location = find_url.split("@")[1]
                    lat = geo_location.split(",")[0]
                    lag = geo_location.split(",")[1]
                    in_semi_part = store_soup.find("section",{"class": "directions"})
                    store = []
                    temp_storeaddresss = list(in_semi_part.stripped_strings)
                    location_name = temp_storeaddresss[1]
                    street_address = temp_storeaddresss[2]
                    city_state = temp_storeaddresss[3]
                    city = city_state.split(",")[0]
                    state_zip = city_state.split(",")[1]
                    state = state_zip.split(" ")[1]
                    store_zip = state_zip.split(" ")[2]
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(store_zip)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(lat)
                    store.append(lag)
                    store.append("<MISSING>")
                    store.append(page_url)
                    yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
