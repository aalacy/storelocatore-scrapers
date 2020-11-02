import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('balduccis_com')





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

    # logger.info("soup ===  first")

    base_url = "https://www.balduccis.com"
    r = session.get("https://www.balduccis.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

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
    location_type = "balduccis"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    location_url_list = []

    for script in soup.find_all('div', {'class': 'views-row'}):
        # address_list = list(script.stripped_strings)
        location_url = base_url + script.find('a')['href']

        if location_url in location_url_list:
            continue

        location_url_list.append(location_url)
        # logger.info("location_url === " + str(location_url))

        r_location = session.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        try:
            hours_of_operation = ",".join(list(soup_location.find('div',{'class':'location-info-hours'}).stripped_strings))
        except:
            hours_of_operation = "<MISSING>"

        try:
            phone = ",".join(list(soup_location.find('div',{'class':'field field--name-field-phone field--type-string field--label-inline'}).find('div',{'class':'field__item'}).stripped_strings))
        except:
            phone = "<MISSING>"


        full_address_url = soup_location.find('div',{'class':'field field--name-field-full-address field--type-string field--label-hidden field__item'}).find('iframe')['src']
        # logger.info("hourse === "+str(full_address_url))

        geo_request = session.get(full_address_url,headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                geo_data = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]

        # logger.info("geo_data ===== "+ geo_data)
        street_address = ",".join(geo_data.split(',')[:-3])
        city = geo_data.split(',')[-3]
        location_name = city
        state = geo_data.split(',')[-2].strip().split(' ')[0]
        zipp = geo_data.split(',')[-2].strip().split(' ')[1]
        latitude = lat
        longitude = lng


        if hours_of_operation is None or len(hours_of_operation) == 0:
            hours_of_operation = "<MISSING>"
        # logger.info("street_address ==== "+ street_address)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
