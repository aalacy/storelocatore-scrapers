import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
# logger = SgLogSetup().get_logger('donnakaran_com')
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
    base_url = "https://www.donnakaran.com"
    r = session.get(base_url + "/store-locator/all-stores.do")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"ml-storelocator-item-wrapper"}):
        store = []
        name = location.find("div",{"class":"eslStore ml-storelocator-headertext"}).text
        try:
            address1 = location.find("div",{"class":"eslAddress1"}).text
            try:
                address2 = location.find("div",{"class":"eslAddress2"}).text
            except:
                address2 = ""
            street_address = address1 + address2
        except:
            address2 = location.find("div",{"class":"eslAddress2"}).text
            address3 = location.find("div",{"class":"eslAddress3"}).text
            street_address = address2 + address3
        city = location.find("span",{"class":"eslCity"}).text.split(",")[0]
        state = location.find("span",{"class":"eslStateCode"}).text
        zip_code = location.find("span",{"class":"eslPostalCode"}).text
        phone = location.find("a",{"class":"eslPhone"}).text.strip()
        store.append("https://www.donnakaran.com")
        store.append(name)
        store.append(street_address.replace("Temporarily Closed",""))
        store.append(city)
        store.append(state.strip())
        store.append(zip_code)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("donna karan")
        url = location.find("div",{"class":"eslStore ml-storelocator-headertext"}).find("a")["href"]
        location_request = session.get(base_url + url)
        location_soup = BeautifulSoup(location_request.text,"html5lib")
        for script in location_soup.find_all("script"):
            if 'location":' in script.text:
                # logger.info(script.text.split('location":')[1].split('"longitude":')[1].split("}")[0])
                store.append(script.text.split('location":')[1].split('"latitude":')[1].split(",")[0])
                store.append(script.text.split('location":')[1].split('"longitude":')[1].split("}")[0])
        store.append("<MISSING>")
        store.append(base_url + url)
        return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
