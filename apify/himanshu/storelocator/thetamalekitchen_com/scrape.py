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

    base_url = "https://www.thetamalekitchen.com"
    r = session.get("https://www.thetamalekitchen.com/locations", headers=headers)
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
    location_type = "thetamalekitchen"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find('div', {'class': 'style-jskuum6dinlineContent'}).find_all('div', {'class': 'txtNew'}):
        list_store_data = list(script.stripped_strings)

        print(str(len(list_store_data)) + ' = list_store_data === ' + str(list_store_data))
        street_address = list_store_data[0].split(',')[0]

        hours_of_operation = '<MISSING>'
        phone = '<MISSING>'

        for element in list_store_data:
            if '(' in element:
                phone = element.split(' (')[0]

            elif '-' in element and 'pm' in element:
                if '<MISSING>' in hours_of_operation:
                    hours_of_operation = ",".join(list_store_data[list_store_data.index(element):])
                    if '(' in hours_of_operation:
                        hours_of_operation = hours_of_operation[:hours_of_operation.find(',(')]

        # hours_of_operation = ",".join(list_store_data[2:])
        country_code = 'US'

        if len(list_store_data[0].split(',')) == 2:
            state = list_store_data[0].split(',')[1].strip().split(' ')[0]
            zipp = list_store_data[0].split(',')[1].strip().split(' ')[1]
            city = '<MISSING>'
        elif len(list_store_data[0].split(',')) == 3:
            state = list_store_data[0].split(',')[2].strip().split(' ')[0]
            zipp = list_store_data[0].split(',')[2].strip().split(' ')[1]
            city = list_store_data[0].split(',')[1]
        else:
            city = list_store_data[1].split(',')[0]
            state = list_store_data[1].split(',')[1].strip().split(' ')[0]
            zipp = list_store_data[1].split(',')[1].strip().split(' ')[1]

        latitude = '<MISSING>'
        longitude = '<MISSING>'
        location_name = city

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
