import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
    'content-type': "application/x-www-form-urlencoded",
    }
    base_url = "https://encompasshealth.com"
    json_data = session.get("https://encompasshealth.com/api/locationservice/locationsearchresults/no_facet/21.190439,72.87756929999999/1000/1/75000").json()['data']['locationDetailsSearchResponse']
    for data in json_data:
        location_name = data['title']
        try:
            street_address = (data['address']['address1'] +" "+ str(data['address']['address2'])).replace("None","").replace("2nd Floor","").replace(",","").strip()
        except:
            street_address = "<MISSING>"
        if "Suite" in street_address:
            street_address = street_address.split("Suite")[0]
        city = data['address']['city']
        state = data['address']['state']  
        zipp =  data['address']['zip']
        if zipp:
            zipp = zipp.replace(".","").replace("178603","78603")
        try:
            phone = data['phone'][0]['value']
        except:
            phone = "<MISSING>"
        latitude = data['coordinates']['latitude']
        longitude = data['coordinates']['longitude']
        page_url = base_url + data['urls'][0]['link']
        try:
            r1 = session.get(page_url)
        except:
            pass
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            hours = " ".join(list(soup1.find("div",{"class":"col-lg-12 col-sm-6 col-lg-12"}).find("ul").find("li",{"class":"info-mb"}).stripped_strings))
        except:
            hours = "<MISSING>"

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data == "+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
