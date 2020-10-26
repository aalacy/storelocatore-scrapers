import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import calendar
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rickersrewards_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    return_main_object = []
    addresses = []

    headers = {'Accept': '* / *',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
               }

    # it will used in store data.
    locator_domain = "https://getgocafe.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "rickersrewards"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    skip = 0

    isFinish = False
    while isFinish is not True:
        r = session.get(
            "https://getgocafe.com/api/sitecore/locations/getlocationlistvm?q=banner:(code+(GG))&skip=" + str(skip) + "&top=5&orderBy=geo.distance(storeCoordinate,%20geography%27POINT(72.8302%2021.1959)%27)%20asc", headers=headers)
        # logger.info("json==" + r.text)
        # # logger.info(str(page))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        json_data = r.json()

        if skip > 262:
            isFinish = True
            break

        else:
            if json_data['Locations'] != []:
                for x in json_data['Locations']:
                    location_name = x['Name']
                    if x['Address']['lineTwo'] == None or x['Address']['lineTwo'] == '-':
                        street_address = x['Address']['lineOne']
                        # logger.info(street_address)
                    else:
                        street1 = x['Address']['lineOne']
                        street2 = x['Address']['lineTwo']
                        street12 = street1, street2
                        street_address = " ".join(street12)
                        # logger.info(street_address)
                    city = x['Address']['City']
                    state = x['Address']['State']['Abbreviation']
                    zipp = x['Address']['Zip']
                    latitude = x['Address']['Coordinates']['Latitude']
                    longitude = x['Address']['Coordinates']['Longitude']
                    # logger.info(city, state, latitude, longitude)
                    phone1 = x['TelephoneNumbers']
                    ph = [y['DisplayNumber']
                          for y in phone1 if 'DisplayNumber' in y]
                    phone = "  or  ".join(ph)
                    # logger.info(phone)

                    hour1 = x['HoursOfOperation']
                    # h1 = [y['DayNumber']
                    #       for y in hour1 if 'DayNumber' in y]
                    hours = [y['HourDisplay']
                             for y in hour1 if 'HourDisplay' in y]
                    # hours_of_operation = "  ".join(hours)
                    day = list(calendar.day_abbr)

                    hours_of_operation = day[0] + "   " + hours[0] + "  " + day[1] + "   " + hours[1] + "  " + day[2] + "   " + hours[2] + "  " + day[3] + \
                        "   " + hours[3] + "  " + day[4] + "   " + hours[4] + "  " + \
                        day[5] + "   " + hours[5] + "  " + \
                        day[6] + "   " + hours[6]
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation]
                    store = ["<MISSING>" if x == "" else x for x in store]
                    logger.info("data = " + str(store))
                    logger.info(
                        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                    return_main_object.append(store)

        skip += 5
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
