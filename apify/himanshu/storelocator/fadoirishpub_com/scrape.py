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

    base_url = "https://fadoirishpub.com"
    r = session.get("https://fadoirishpub.com/locations/", headers=headers)
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
    location_type = "fadoirishpub"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    for script in soup.find_all('div', {'class': 'location-content'}):
        list_store_detail = list(script.stripped_strings)

        if 'Go To Pub' in list_store_detail:
            list_store_detail.remove('Go To Pub')

        location_name = list_store_detail[0]
        street_address = list_store_detail[-3]
        phone = list_store_detail[-1].split('|')[0].strip()
        city = list_store_detail[-2].split(',')[0]
        state = list_store_detail[-2].split(',')[1].strip().split(' ')[0]
        zipp = list_store_detail[-2].split(',')[1].strip().split(' ')[1]
        country_code = 'US'

        if not zipp.isdigit():
            continue

        store_url = script.find('a')['href']
        r_store = session.get(store_url, headers=headers)
        soup_store = BeautifulSoup(r_store.text, "lxml")
        # print('Store URL = ' + store_url)

        list_hour = list(soup_store.find('div',{'class':'info-box'}).stripped_strings)
        # print('list_hour = ' + str(list_hour))

        if '(Click for kitchen hours)' in list_hour:
            hours_of_operation = ",".join(list_hour[:list_hour.index('(Click for kitchen hours)')])
        elif 'KITCHEN HOURS' in list_hour:
            hours_of_operation = ",".join(list_hour[:list_hour.index('KITCHEN HOURS')])
        else:
            hours_of_operation = ",".join(list_hour[:list_hour.index('(')])
        print('Hours list  = ' + str(hours_of_operation))


        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
