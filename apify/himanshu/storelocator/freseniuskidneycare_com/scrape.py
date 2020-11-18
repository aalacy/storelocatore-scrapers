import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('freseniuskidneycare_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)      

def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.freseniuskidneycare.com"
    page_number = 1
    while True:
        location_url = "https://www.freseniuskidneycare.com/dialysis-centers?lat=40.7987048&lng=-73.6506776&radius=250&page="+ str(page_number)
   
        location_soup = BeautifulSoup(session.get(location_url, headers=headers).text, "lxml")
        if location_soup.find("tr",{"class":"locator-results-item js-locator-item js-loadmore-item"}) == None:
            break
        for data in location_soup.find_all("tr",{"class":"locator-results-item js-locator-item js-loadmore-item"}):
            location_name = data['data-clinicname'].split(".")[1].strip()
            street_address = data['data-clinicaddr1']
            if data['data-clinicaddr2']:
                street_address+=" "+ data['data-clinicaddr2']
            city = data['data-clinicaddr3'].split(",")[0].strip()
            state = data['data-clinicaddr3'].split(",")[1].strip()
            zipp = data['data-clinicaddr3'].split(",")[2].strip()
            if zipp == "00765":
                continue
            page_url = base_url + data['data-clinicdetailsurl']
            store_number = page_url.split("/")[-1]
            latitude = data['data-coords'].split(",")[0]
            longitude = data['data-coords'].split(",")[1]
            phone = data.find("td",{"class":{"locator-phone-list"}}).find_all("div")[1].find("a").text.strip()
            hours = " ".join(list(data.find_next("tr").find("div",{"class":"locator-results-item--more__hours-details"}).stripped_strings))
            location_type = "MedicalClinic"

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            # logger.info('---store--'+str(store))
            yield store
        page_number += 1




def scrape():
    data = fetch_data()
    write_output(data)
scrape()

