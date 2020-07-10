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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://crenospizzaco.com/"
    json_data = session.get("https://crenospizzaco.com/wp-admin/admin-ajax.php?action=store_search&lat=41.17737&lng=-80.97606&max_results=100&search_radius=500",headers=headers).json()  
    for data in json_data:
        location_name = data['store'].replace("&#8211;","-")
        street_address = (data['address'] +" "+ str(data['address2'])).strip()
        city = data['city']
        state = data['state']
        zipp = data['zip']
        country_code = data['country']
        # store_number = data['id']
        phone = data['phone']
        location_type = "<MISSING>"
        lat = data['lat']
        lng =data['lng']
        hours = "<MISSING>"
        page_url = data['url']
        if "Caldwell" in location_name:
            page_url = "https://crenospizzaco.com/caldwell/"
        tem_var = []
        tem_var.append("https://crenospizzaco.com")
        tem_var.append(location_name)
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipp)
        tem_var.append(country_code)
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append(location_type)
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append("<MISSING>")
        tem_var.append(page_url)
        yield tem_var
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


