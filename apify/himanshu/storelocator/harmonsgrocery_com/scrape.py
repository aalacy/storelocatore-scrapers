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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "http://harmonsgrocery.com/"
    r = session.get("https://www.harmonsgrocery.com/wp-admin/admin-ajax.php?action=get_ajax_posts&nextNonce=34695cf658", headers=headers).json()
    for data in r:
        location_name = data['name']
        street_address = data['address'].split("<br />")[0].split("<p>")[1]
        city = data['address'].split("<br />")[1].split("</p>")[0].split(",")[0].strip()
        state = data['address'].split("<br />")[1].split("</p>")[0].split(",")[1].split(" ")[1]
        zipp = data['address'].split("<br />")[1].split("</p>")[0].split(",")[1].split(" ")[2]
        phone = data['address'].split("<p>")[2].replace("</p>",'').strip()
        hours_of_operation = " ".join(list(BeautifulSoup(data['address'], "lxml").find_all("p")[-1].stripped_strings))
        latitude = data['latitude']
        longitude = data['longitude']
        
        store =[]
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(" https://www.harmonsgrocery.com/locations")
        # print("data====="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        yield store

    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


