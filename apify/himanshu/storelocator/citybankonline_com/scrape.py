import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.city.bank"
    r = session.get("https://www.city.bank/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find("div",{'class':"sf_cols"}).find_all("a"):
        # print(base_url + location["href"])
        try:
            location_request = session.get(base_url + location["href"],headers=headers)
        except:
            continue
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{"class":"main-content"}).find('div',{'class':"sfContentBlock"}).stripped_strings)
        if location_details == []:
            location_details = list(location_soup.find("div",{"class":"main-content"}).find_all('div',{'class':"sfContentBlock"})[1].stripped_strings)
        if re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",location_details[2]) == []:
            location_details[1] = location_details[1] + " " + location_details[2]
            del location_details[2]
        state_split = re.findall("([A-Z]{2})",location_details[2])
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"
        store_zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",location_details[2])
        if store_zip_split:
            store_zip = store_zip_split[-1]
        else:
            store_zip = "<MISSING>"
        hours = " ".join(list(location_soup.find("div",{'class':"sf_colsOut col-left"}).stripped_strings))
        phone = ""
        for detail in location_details:
            if re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),detail):
                phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),detail)[-1]
        geo_location = location_soup.find_all("iframe")[-1]["src"]
        store = []
        store.append("https://citybankonline.com")
        store.append(location.text.strip())
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append(hours.replace("\t"," "))
        store.append(base_url + location["href"])
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # print(store)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
