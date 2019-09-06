import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def get_store(country_code):
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://www.brunellocucinelli.com"
    usa_request = requests.get("https://shop.brunellocucinelli.com/on/demandware.store/Sites-bc-us-Site/en_US/Stores-CalculateStores?mycountry=" + country_code + "&urlStore=",headers=headers)
    usa_soup = BeautifulSoup(usa_request.text,"lxml")
    country_data = []
    location_data = json.loads(usa_soup.find("script").text.split("locations = ")[2].split("];")[0].replace("\n","").replace("'",'"')[:-2] + "]]")
    for location in usa_soup.find_all("div",{'class':"store-details-wrap"}):
        store = []
        store.append("http://www.brunellocucinelli.com")
        store.append(location["data-storename"])
        store.append(location.find("p",{'class':"store-address1"}).text)
        store.append(location.find("p",{'class':"store-city"}).text)
        store.append(list(location.find("p",{'class':"store-address2"}).stripped_strings)[0].split("\n")[0])
        store.append(list(location.find("p",{'class':"store-address2"}).stripped_strings)[0].split("\n")[-1])
        store.append(country_code)
        store.append(location["data-id"])
        store.append(list(location.find("tr",{'class':"store-phone"}).stripped_strings)[1])
        store.append("brunello cucinelli")
        for i in range(len(location_data)):
            if str(location_data[i][0]) == str(location["data-id"]):
                lat = location_data[i][1]
                lng = location_data[i][2]
        store.append(lat)
        store.append(lng)
        store.append(" ".join(list(location.find("p",{'class':'store-hours'}).stripped_strings)))
        country_data.append(store)
    return country_data

def fetch_data():
    return_main_object = []
    us_data = get_store("US")
    return_main_object.extend(us_data)
    ca_data = get_store("CA")
    return_main_object.extend(ca_data)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
