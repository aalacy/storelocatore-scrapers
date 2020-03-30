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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://wingspizzanthings.com/"
    r = session.get("http://wingspizzanthings.com/locations.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for map_part in soup.find_all("map",{'id':re.compile("map")}):
        for location in map_part.find_all("area",{"href":re.compile(".")}):
            location_request = session.get(base_url + location['href'],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("div",{'id':"divMain"}).find("img",{"alt":re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")}):
                location_text = location_soup.find("div",{'id':"divMain"}).find("img",{"alt":re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")})["alt"]
                street_address = " ".join(location_text.split(",")[0].split(" ")[:-1])
                city = location_text.split(",")[0].split(" ")[-1]
                zip_split =  re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",location_text)
                if zip_split:
                    store_zip = zip_split[-1]
                state_split = re.findall("([A-Z]{2})",location_text)
                if state_split:
                    state = state_split[-1]
                else:
                    state = "<MISSING>"
                phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),location_text)[-1]
                store = []
                store.append("http://wingspizzanthings.com")
                store.append("<MISSING>")
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(store_zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(base_url + location['href'])
                yield store
            for store in location_soup.find("div",{'id':"divMain"}).find_all("div",recursive=False):
                if len(store.find_all("p",{"class":"Address"})) > 1:
                    location_details = list(store.stripped_strings)
                    if len(location_details) < 3:
                        continue
                    if len(location_details[3].split(",")) == 1:
                        location_details.insert(1,"")
                    store = []
                    store.append("http://wingspizzanthings.com")
                    store.append(" ".join(location_details[0:2]))
                    store.append(location_details[2])
                    store.append(location_details[3].split(",")[0])
                    store.append(location_details[3].split(",")[1].split(" ")[-2])
                    store.append(location_details[3].split(",")[1].split(" ")[-1])
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(" ".join(location_details[4:7]).replace("Phone: ","").replace("FOOD ","").split("Fax")[0] if len(location_details) > 5 else " ".join(location_details[4:6]).replace("Phone: ","").replace("FOOD ","").split("Fax")[0])
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(base_url + location['href'])
                    yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
