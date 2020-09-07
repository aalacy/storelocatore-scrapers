import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.rachellebery.ca"
    r = session.get("https://www.rachellebery.ca/trouver-un-magasin/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    # datapath_url = soup.text.split('datapath":"')[1].split('"')[0].replace("\\", "")
    temp_url = "https://www.api-sobeys.com/magasins/stores_locator/MmE4ZTZiNjIzMWYzMzU2YTA4ZDBiZWIzNTdmMGQyOTA2ODk5YTNlNjQ3ZTBlMmM4NjVkYTA2YzU2NzA3Nzg1MmU0NGRhNjkwMWUwMjYyZThlZjMzZWU4YTRiM2E3OTVjMDk4ODUyZWE2MmIwNDEzZDQzN2VjMzU5ZmVlMDlkM2NLeDV0R2VORUhadENvME0wR25KWnZVcWhwMWRSTDc5WkJiaDlaMDBMVW9CMzRTc0VkVlpaRGZBbWU0RWNLTGVj/1822?origLat=45.5115686&origLng=-73.5936926&origAddress=Mount+Royal+Mountain%2C+Canada%2C+1576+Voie+Camillien-Houde%2C+Montreal%2C+QC+H2W+1S8%2C+Canada&formattedAddress=&boundsNorthEast=&boundsSouthWest="

    r1 = session.get(temp_url, headers=headers,verify=False)

    json_data = r1.json()

    arr_street_address = []
    for data in json_data:

        if data["address"] in street_address:
            continue

        latitude = data["lat"]
        longitude = data["lng"]
        street_address = data["address"]
        arr_street_address.append(street_address)

        city = data["city"]
        location_name = data['name']+" at "+city
        state = data["state"]
        zipp = data["postal"]
        phone = data["phone"]
        country_code = 'CA'
        store_number = data['id']
        page_url = "https://www.rachellebery.ca/magasin/" + str(store_number) + "/"

        day_list = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        hoursfrom_list = data["hours1"].split(',')
        hoursto_list = data["hours2"].split(",")

        hours_of_operation = ""
        for i in range(len(day_list)):
            hours_of_operation += day_list[i] + " : " + hoursfrom_list[i] + "-" + hoursto_list[i] + ", "

        hours_of_operation = hours_of_operation[:-2]

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
