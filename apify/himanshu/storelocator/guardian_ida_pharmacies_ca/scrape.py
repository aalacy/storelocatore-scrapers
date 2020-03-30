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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # print("soup ===  first")

    base_url = "https://www.guardian-ida-pharmacies.ca"
    r = session.get("https://www.guardian-ida-pharmacies.ca/en/find-a-pharmacy", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

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
    location_type = "guardian-ida-pharmacies"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    location_url = base_url + soup.find('div',{'class':'pharmacy-map loading'})['data-pharmacies-url']
    r_location = session.get(location_url, headers=headers)
    location_json = r_location.json()

    for location_list in location_json['pharmacies']:
        # print("data === " + str(location_list))

        latitude = location_list['location']['latitude']
        longitude = location_list['location']['longitude']
        location_name = location_list['title']
        phone = location_list['phone']
        store_number = location_list['storeCode']
        street_address = location_list['address'].split(',')[0]
        city = location_list['address'].split(',')[1]
        state = location_list['address'].split(',')[-2].replace('(',"").replace(')',"")
        zipp = location_list['address'].split(',')[-1]
        hours_data = location_list['storeOpeningHours']
        country_code = 'CA'

        hours_of_operation = ""
        for days_data in hours_data:
            # if 'start' in days_data and 'end' in days_data:
            if days_data['start'] is not None:
                hours_of_operation += str(days_data['day']) +" = "+ str(days_data['start']) +" - "+ str(days_data['end']) +" ,"
            else:
                hours_of_operation += str(days_data['day']) +" = Closed ,"

        if len(hours_of_operation) > 1:
            hours_of_operation = hours_of_operation[:-1]
        else:
            hours_of_operation = "<MISSING>"

        if phone is None or len(phone) == 0:
            phone = "<MISSING>"
        # print("hours === "+ hours_of_operation)

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
