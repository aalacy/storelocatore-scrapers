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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*"
    }

    data = 'action=location_finder&new_lat=40.7226698&new_lng=-73.51818329999998&type=All+Stores&address=Location+Search+-+Near%3A+%E2%80%98Levittown%2C+NY+11756%2C+USA%E2%80%99&access=true&offset=0&ppp=50000&post_id=33'
    r = session.post("https://stores.reebok.com/wp-admin/admin-ajax.php",headers=headers,data=data)
    soup = BeautifulSoup(r.text,"lxml")

    for location in soup.find_all("div",{"class":"content"}):
        address = location.find("div",{"class":"address"}).text.strip()
        store_zip_split = re.findall("([0-9]{5})",address)
        if store_zip_split:
            store_zip = store_zip_split[-1]
        state_split = re.findall("([A-Z]{2}) ",address)
        if state_split:
            state = state_split[-1]
        name = location.find("h1").text.strip()
        hours = " ".join(list(location.find("div",{"class":"hours"}).stripped_strings))
        phone = list(location.find("div",{"class":"contact"}).stripped_strings)
        # some time address come as 651 Kapkowski Road, Suite 1048, Elizabeth, NJ 07201 and 1288 The Arches Circle, Deer Park, NY 11729
        city = address.split(",")[-2]
        street_address = ",".join(address.split(",")[:-2])
        store = []
        store.append("https://www.reebok.com")
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[-1] if phone != [] else "<MISSING>")
        if store[-1][0] == "0":
            store[-1] = store[-1][1:]
        store.append("reebok")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours if hours != "" else "<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()