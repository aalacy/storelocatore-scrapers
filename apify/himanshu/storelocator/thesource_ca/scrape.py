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
    base_url = "https://www.thesource.ca"
    r = session.get("https://www.thesource.ca/en-ca/store-finder?latitude=43.0&longitude=-79.0&q=&popupMode=false&show=All",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    number_page = int(soup.find("span",{"class":"maxNumberOfPages"}).text)
    for i in range(number_page):
        page_request = session.get("https://www.thesource.ca/en-ca/store-finder?latitude=43.0&longitude=-79.0&q=&popupMode=false&page=" + str(i) + "&show=All",headers=headers)
        page_soup = BeautifulSoup(page_request.text,"lxml")
        geo_locations = page_soup.find("div",{"id":"map_canvas"})["data-stores"]
        location_list = json.loads(geo_locations)
        for location in page_soup.find_all("tr",{"class":"storeItem store-result-row"}):
            name = location.find("a").text
            address = list(location.find("ul").stripped_strings)
            phone = location.find("p").text.strip()
            if location.find("td",{"class":"hours"}) == None:
                continue
            hours = " ".join(list(location.find("td",{"class":"hours"}).stripped_strings))
            for key in location_list:
                if name == location_list[key]["name"]:
                    lat = location_list[key]["latitude"]
                    lng = location_list[key]["longitude"]
                    store_id = location_list[key]["id"]
                    del location_list[key]
                    break
            store = []
            store.append("https://www.thesource.ca")
            store.append(name)
            store.append(" ".join(address[0:-2]))
            store.append(address[-2].split(",")[0])
            store.append(address[-2].split(",")[-1])
            if len(address[-1]) == 6:
                store.append(address[-1][0:3] + " " + address[-1][3:])
            else:
                store.append(address[-1])
            store.append("CA")
            store.append(store_id)
            store.append(phone)
            store.append("the source")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
