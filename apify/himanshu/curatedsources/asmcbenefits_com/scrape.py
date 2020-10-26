import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('asmcbenefits_com')




def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # zips = sgzip.coords_for_radius(50)
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.asmcbenefits.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    for zip_code in zips:
        try:
            q = "zip=" + str(zip_code) + "&distance=100&btnLocate=Locate&distanceType=mi"
            r = requests.get(
                " https://asmcbenefits.com/members/locator.php?" + q, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            if soup.find_all("li", {'class': 'results loc6'}) == []:
                continue
            else:
                # logger.info("zip==" + str(zip_code) + "==map_list==" +
                #       str(soup.find_all("li", {'class': 'results loc6'})))
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                for details in soup.find_all("li", class_="results loc6"):
                    # logger.info(details)
                    # logger.info("~~~~~~~~~~~~~~~~~~~~")
                    info = details.find("p")
                    info_list = list(details.stripped_strings)
                    # logger.info(info_list)
                    location_name = info_list[1]
                    street_address = info_list[2]
                    city = info_list[3].split(',')[0]
                    state = info_list[3].split(',')[1].split()[0]
                    zipp1 = info_list[3].split(',')[1].split()[-1]
                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp1))
                    # logger.info(ca_zip_list)
                    if ca_zip_list:
                        zipp = ca_zip_list[0]
                        country_code = "CA"
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp1))
                    if us_zip_list:
                        zipp = us_zip_list[0]
                        country_code = "US"
                    phone_tag = info_list[4].split('|')[0].encode(
                        'ascii', 'ignore').decode('ascii').strip()
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                    # logger.info(phone_list)
                    if phone_list ==[]:
                        phone = "<MISSING>"
                    else:
                        phone = phone_list[0].strip().replace(')','').replace('(','').strip()
                    # logger.info(phone)
                    latitude = details.find("input", {'id': 'marker_lat'})['value']
                    longitude = details.find(
                        "input", {'id': 'marker_long'})['value']
                    hours_of_operation = details.find(
                        "input", {'id': 'marker_hoursOfOperation'})['value']
                    # logger.info(hours_of_operation)
                    # logger.info(location_name, street_address, city,
                    #       state, zipp, phone, latitude, longitude)
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                    store = ["<MISSING>" if x == "" else x for x in store]

                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    # logger.info("data = " + str(store))
                    # logger.info(
                    #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                    return_main_object.append(store)
        except:
            continue
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
