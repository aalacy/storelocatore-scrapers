import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    addresses = []
    base_url = "https://gomart.com/"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url =""
    r = session.get("https://gomart.com/wp-content/themes/gomart-2020/locations/locations_map_display.php",headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    script =soup.find(lambda tag: (tag.name == "script") and "window.locations" in tag.text).text.split("window.locations =")[1].split('}}];')[0]+"}}]"
    scripts = json.loads(script)
    for info in scripts:
        street_address = " ".join(info['m']['address'])
        location_name = " ".join(info['m']['name'])
        store_number = (location_name.split( )[-1])
        state = " ".join(info['m']['state'])
        zipp = " ".join(info['m']['zip'])
        phone = " ".join(info['m']['phone'])
        city = " ".join(info['m']['city'])
        latitude = " ".join(info['m']['latitude'])
        longitude = " ".join(info['m']['longitude'])
        location_type = "<MISSING>"
        country_code = "US"
        store_number = store_number
        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
