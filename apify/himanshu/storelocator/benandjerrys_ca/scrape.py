import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    for zip_code in zips:
        # print(zip_code)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        base_url = "https://www.benandjerrys.ca"

        # zip_code = 11576

        r = requests.get(
            "https://benjerry.where2getit.com/ajax?lang=en_US&xml_request=%3Crequest%3E%20%3Cappkey%3E3D71930E-EC80"
            "-11E6-A0AE-8347407E493E%3C/appkey%3E%20%3Cformdata%20id=%22locatorsearch%22%3E%20%3Cdataview"
            "%3Estore_default%3C/dataview%3E%20%3Climit%3E10000%3C/limit%3E%20%3Cgeolocs%3E%20%3Cgeoloc%3E%20"
            "%3Caddressline%3E" + str(
                zip_code) + "%3C/addressline%3E%20%3C/geoloc%3E%20%3C/geolocs%3E%20%3Csearchradius%3E100%3C"
                            "/searchradius%3E%20%3C/formdata%3E%20%3C/request%3E",
            headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

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
        location_type = "benandjerrys"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        raw_address = ""
        hours_of_operation = "<MISSING>"

        for script in soup.find_all("poi"):

            location_name = script.find('name').text
            street_address = script.find('address1').text + " " + script.find('address2').text
            city = script.find('city').text
            state = script.find('state').text
            zipp = script.find('postalcode').text
            country_code = script.find('country').text
            latitude = script.find('latitude').text
            longitude = script.find('longitude').text
            phone = script.find('cakephone').text.replace('&#xa0;', "")

            if len(location_name.strip()) == 0:
                location_name = "<MISSING>"

            if len(street_address.strip()) == 0:
                street_address = "<MISSING>"

            if len(city.strip()) == 0:
                city = "<MISSING>"

            if len(state.strip()) == 0:
                state = "<MISSING>"

            if len(zipp.strip()) == 0:
                zipp = "<MISSING>"

            if len(country_code.strip()) == 0:
                country_code = "US"

            if len(latitude.strip()) == 0:
                latitude = "<MISSING>"

            if len(longitude.strip()) == 0:
                longitude = "<MISSING>"

            if len(phone.strip()) == 0:
                phone = "<MISSING>"

            if len(script.find('sunday').text) > 0 or len(script.find('monday').text) > 0 \
                    or len(script.find('tuesday').text) > 0 or len(script.find('wednesday').text) > 0 \
                    or len(script.find('thursday').text) > 0 or len(script.find('friday').text) > 0 \
                    or len(script.find('saturday').text) > 0:
                hours_of_operation = "Sunday = " + script.find('sunday').text + ", " + \
                                     "Monday = " + script.find('monday').text + ", " + \
                                     "Tuesday = " + script.find('tuesday').text + ", " + \
                                     "Wednesday = " + script.find('wednesday').text + ", " + \
                                     "Thursday = " + script.find('thursday').text + ", " + \
                                     "Friday = " + script.find('friday').text + ", " + \
                                     "Saturday = " + script.find('saturday').text
            else:
                hours_of_operation = "<MISSING>"

            # print("hours_of_operation === "+str(hours_of_operation))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if store[2] + store[-3] not in addresses:
                addresses.append(store[2] + store[-3])

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
