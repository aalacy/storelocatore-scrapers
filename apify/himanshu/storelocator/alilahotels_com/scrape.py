import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.alilahotels.com"
    r = session.get("https://www.alilahotels.com/destinations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for country in soup.find_all("div",{'class':"footer__column grid__item footer__column--destinations"}):
        if "United States" in list(country.stripped_strings):
            for location in country.find('ul',{'class':"js-list-content footer__list"}).find_all("li",{'class':"footer__list-item"}):
                page_url = location.find("a")["href"]
                location_request = session.get(page_url,headers=headers)
                location_soup = BeautifulSoup(location_request.text,'lxml')
                location_details = json.loads(location_soup.find("script",{'type':"application/ld+json"}).text)
                store = []
                store.append(base_url)
                store.append(location_details['name'])
                store.append(location_details["address"]["streetAddress"].split(",")[0])
                store.append(location_details["address"]["addressLocality"] if location_details["address"]["addressLocality"] != "" else "<MISSING>")
                store.append(location_details["address"]["addressRegion"] if location_details["address"]["addressRegion"] != "" else "<MISSING>")
                store.append(location_details["address"]["postalCode"] if location_details["address"]["postalCode"] != "" else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(location_details["telephone"])
                store.append("alila")
                store.append(location_details["geo"]["latitude"])
                store.append(location_details["geo"]["longitude"])
                store.append("<MISSING>")
                store.append(page_url)
                return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
