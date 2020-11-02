import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('earthbar_com')




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
    base_url = "https://earthbar.com/apps/store-locator"
    page_url = "https://earthbar.com/apps/store-locator"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    store_listing = soup.find("div",{"id": "addresses_list"}).find('ul').find_all('li')
    for lit in store_listing:
        location_type = lit.find('span',class_='name').text.strip()
        store_no=lit['onmouseover'].split('(')[-1].split(')')[0].strip()
        address=lit.find('a').find('span',{"class":"address"}).text.strip()
        city=lit.find('a').find('span',{"class":"city"}).text.strip()
        state=lit.find('a').find('span',{"class":"prov_state"}).text.strip()
        zip=lit.find('a').find('span',{"class":"postal_zip"}).text.strip()
        country=lit.find('a').find('span',{"class":"country"}).text.strip()
        try:
            phone=lit.find('a').find('span',{"class":"phone"}).text.strip()
        except:
            phone="<MISSING>"
        try:
            store_name=lit.find('a').find('span',{"class":"hours"}).text.split('Store Name:')[-1].strip()
        except:
            store_name="<MISSING>"
        if(country=="United States"):
            country="US"
        store = []
        store.append("https://earthbar.com/")
        store.append(store_name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append(store_no)
        store.append(phone)
        store.append(location_type)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        #logger.info(str(store))
        #logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
