import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    base_url = "https://www.justtires.com"
    try:
        r = requests.get("https://www.justtires.com/en-US/service-center-near-me",headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        for state in soup.find("div",{'class':"browse-by-state-wrapper__list"}).find_all("a"):
            # print(base_url + state["href"])
            state_request = requests.get(base_url + state["href"],headers=headers)
            state_soup = BeautifulSoup(state_request.text,"lxml")
            for city in state_soup.find("div",{'class':"browse-by-state-wrapper__list"}).find_all("a"):
                # print(base_url + city["href"])
                city_request = requests.get(base_url + city["href"],headers=headers)
                city_soup = BeautifulSoup(city_request.text,"lxml")
                for location in city_soup.find_all("li",{"class":'store-results__results__item'}):
                    page_url = base_url + location.find("a")["href"]
                    # print(page_url)
                    if location.find("p",{"class":"my-store__direction"}) == None:
                        continue
                    address = json.loads(location.find("p",{"class":"my-store__direction"})["data-location"])
                    location_request = requests.get(page_url,headers=headers)
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                    name = location_soup.find("span",{'itemprop':"name"}).text.strip()
                    store_id = location_soup.find("div",{"data-mobile-store":"store"})["data-store-id"]
                    phone = location_soup.find("span",{'itemprop':"telephone"}).text.strip()
                    store = []
                    store.append("https://www.justtires.com")
                    store.append(name)
                    store.append(address["street"])
                    store.append(address["city"])
                    store.append(address["state"])
                    store.append(address["zipCode"])
                    store.append(address["country"])
                    store.append(store_id)
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(address["latitude"])
                    store.append(address["longitude"])
                    hours = " ".join(list(location_soup.find("div",{"class":"store-page-masthead__store__wrapper"}).find("div",{"class":"right-column"}).stripped_strings))
                    store.append(hours if hours else "<MISSING>")
                    store.append(page_url)
                    # print(store)
                    yield store
    except:
        pass
def scrape():
    data = fetch_data()
    write_output(data)

scrape()