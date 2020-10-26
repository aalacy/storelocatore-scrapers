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

    base_url = "https://jonsmithsubs.com"
    r = session.get("https://jonsmithsubs.com/locations/", headers=headers)
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
    location_type = "jonsmithsubs"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find_all("div", {'class': re.compile('col-xs-12 col-sm-6 col-md-3 item')}):
        store_url = base_url + script.find('h2').find('a')['href']

        print("store_url == "+store_url)

        latitude = script['data-location'].split(',')[0]
        longitude = script['data-location'].split(',')[1]
        location_name = script.find('h2').find('a').text

        # print("latitude = " + latitude)
        # print("longitude = " + longitude)
        # print("location_name = " + location_name)
        # print("url = " + store_url)

        r_store = session.get(store_url, headers=headers)
        soup_store = BeautifulSoup(r_store.text, "lxml")

        for script_store in soup_store.find_all("ul", {'class': 'loc'}):

            if script_store.find('li', {'class': re.compile('phonenum')}) is not None:
                phone = script_store.find('li', {'class': re.compile('phonenum')}).find('strong').text
            else:
                phone = '<MISSING>'

            if script_store.find('li', {'class': 'address'}) is not None:
                address = list(script_store.find('li', {'class': 'address'}).stripped_strings)
                street_address = address[0]
                city = address[1].split(',')[0]
                zipp = address[1].split(',')[1].split(' ')[-1]
                state = address[1].split(',')[1].split(' ')[-2]
            else:
                address = '<MISSING>'
                city = '<MISSING>'
                zipp = '<MISSING>'
                state = '<MISSING>'

            hours_of_operation = ",".join(list(soup_store.find("div", {'class': 'col-xs-12 col-md-4 equal locinfo second'}).stripped_strings))
            country_code = 'US'
            store_number = '<MISSING>'

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
