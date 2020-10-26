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

    base_url = "https://www.brothersbar.com"
    r = session.get("https://www.brothersbar.com/", headers=headers)
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
    location_type = "brothersbar"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    json_uri_list = soup.text.split('"pageList":')[1].split('}]')[0] + '}]}'
    json_uri_list = json.loads(json_uri_list)

    for link_data in json_uri_list['pages']:
        if '-' not in link_data['pageUriSEO']:
            location_url = base_url + '/' + link_data['pageUriSEO']
            # print('location_url === ' + str(location_url))

            r_location = session.get(location_url, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")

            tag_hours = soup_location.find(lambda tag: tag.name == "span" and "hours:" in tag.text.lower())
            if tag_hours is None:
                continue
            tag_hours = tag_hours.parent.parent
            hours_of_operation = ','.join(list(tag_hours.stripped_strings))

            tag_address = soup_location.find(
                lambda tag: tag.name == "span" and "brothers bar & grill" in tag.text.lower())
            tag_address = tag_address.parent.parent
            list_address = list(tag_address.stripped_strings)

            street_address = list_address[1]
            city = list_address[2].split(',')[0]
            state = list_address[2].split(',')[1].strip().split(' ')[0]
            zipp = list_address[2].split(',')[1].strip().split(' ')[-1]
            phone = list_address[-1]

            location_name = city

            # print('script_hours === ' + str(list_address))

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
