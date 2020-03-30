import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    print("soup ===  first")

    base_url = "https://www.branns.com"
    r = session.get("https://www.branns.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "branns"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find_all('div', {'class': re.compile('et_pb_module et_pb_text et_pb_text')}):
        list_store_data = list(script.stripped_strings)

        print(str(len(list_store_data)) + ' = list_store_data === ' + str(list_store_data))
        if len(list_store_data) > 2:
            location_name = list_store_data[0]
            street_address = list_store_data[1]
            phone = list_store_data[3]
            hours_of_operation = ",".join(list_store_data[4:])
            country_code = 'US'

            city = list_store_data[2].split(',')[0]
            if len(list_store_data[2].split(',')[1].strip().split(' ')) > 1:
                zipp = list_store_data[2].split(',')[1].strip().split(' ')[-1]
                state = list_store_data[2].split(',')[1].strip().split(' ')[-2]
            else:
                zipp = list_store_data[2].split(',')[1].strip().split(' ')[-1]
                state = '<MISSING>'
        else:
            map_location = script.find('a')['href']
            latitude = map_location.split("/@")[1].split(",")[0]
            longitude = map_location.split("/@")[1].split(",")[1]


            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            print("data = " + str(store))
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
