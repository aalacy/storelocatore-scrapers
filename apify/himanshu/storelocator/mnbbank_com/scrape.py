import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {
        'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://mnbbank.com/"
    locator_domain = "https://mnbbank.com/"
    r = session.get(
        "https://mnbbank.com/api/locationfilter?zipcode=&city=", headers=header).json()
    for loc in r['filteredLocations']:
        location_name = loc['locationBranchTitle']
        street_address = " ".join(
            loc['locationAddress'].split(',')[:-3]).strip()
        city = loc['locationAddress'].split(',')[-3].strip()
        state = loc['locationAddress'].split(',')[-2].strip()
        zipp = loc['locationAddress'].split(',')[-1].strip()
        try:
            hours_of_operation = loc['locationLobbyHours'].replace('\n', ' ').strip(
            ) + " " + loc['locationDriveInHours'].replace('\n', ' ').strip()
            phone = loc['locationPhone'].strip()

        except:
            hours_of_operation = "<MISSING>"
            phone = loc['locationPhone'].strip()

        if hours_of_operation == " ":
            hours_of_operation = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "ATM Only" in location_name:
            location_type = "ATM"
        else:
            location_type = "Branch"
        latitude = loc['locationLatitiude']
        longitude = loc['locationLongitude']

        store_number = "<MISSING>"
        country_code = "US"
        page_url = "https://mnbbank.com/about/locations?zipcode=&city="

        # print(hours_of_operation)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if latitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        # print("data == " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
