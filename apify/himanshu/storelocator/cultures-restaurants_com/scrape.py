import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


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
    base_url = "https://cultures-restaurants.com/wp-admin/admin-ajax.php?action=store_search&lat=45.501689&lng=-73.56725599999999&max_results=25&search_radius=50&autoload=1"
    r = session.get(base_url).json()
    return_main_object = []
    for i in range(len(r)):
        store = []
        store.append("https://cultures-restaurants.com")
        store.append(r[i]['store'])
        store.append(r[i]['address'])
        store.append(r[i]['city'])
        store.append(r[i]['state'].strip())
        if r[i]['zip']!="":
            store.append(r[i]['zip'])
        else:
            store.append("<MISSING>")
        if r[i]['country'] =='Canada' or r[i]['country'] == "Cannada":
            store.append("CA")
        else:
            store.append(r[i]['country'])
        store.append(r[i]['id'])
        store.append(r[i]['phone'])
        store.append('Cultures Restaurants')
        store.append(r[i]['lat'])
        store.append(r[i]['lng'])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
