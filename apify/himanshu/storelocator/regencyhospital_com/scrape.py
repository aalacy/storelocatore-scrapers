import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.regencyhospital.com"
    r = session.get("https://www.selectmedical.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    data = json.loads(soup.find("div",{'class':"component search-results col-xs-12 location-cards-list"})["data-properties"])
    s = data["s"]
    item_id = data["itemid"]
    v = data["v"]
    count = 0
    while True:
        location_request = session.get("https://www.selectmedical.com//sxa/search/results/?s="+ s + "&itemid=" + item_id + "&sig=&autoFireSearch=true&v=" + v + "&p=8&e=" + str(count),headers=headers)
        try:
            location_list = location_request.json()["Results"]
        except:
            count = count + 8
            continue
        if location_list == []:
            break
        for store_data in location_list:
            location_soup = BeautifulSoup(store_data["Html"],"lxml")
            name = location_soup.find("span",{'class':"location-title"}).text.strip()
            address = location_soup.find("div",{'class':"address"}).text
            city = location_soup.find("span",{'class':"city"}).text
            state = location_soup.find("span",{'class':"state"}).text
            store_zip = location_soup.find("span",{'class':"zip"}).text
            phone = location_soup.find("div",{'class':"phone-container"}).text.strip()
            geo_location = location_soup.find("img")["data-latlong"]
            store = []
            store.append("https://www.regencyhospital.com")
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone != "" else "<MISSING>")
            store.append("regency hospital")
            store.append(geo_location.split("|")[0])
            store.append(geo_location.split("|")[1])
            store.append("<MISSING>")
            return_main_object.append(store)
        count = count + 8
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
