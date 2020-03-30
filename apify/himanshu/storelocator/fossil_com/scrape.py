import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip



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
        base_url = "https://www.fossil.com"

        r = session.get(
            "https://hosted.where2getit.com/fossil/ajax?&xml_request=%3Crequest%3E%20%3Cappkey%3E269B11D6-E81F-11E3-A0C3-A70A0D516365%3C/appkey%3E%20%3Cformdata%20id=%22locatorsearch%22%3E%20%3Cdataview%3Estore_default%3C/dataview%3E%20%3Climit%3E100000%3C/limit%3E%20%3Cgeolocs%3E%20%3Cgeoloc%3E%20%3Caddressline%3E" + str(
                zip_code) + "%3C/addressline%3E%20%3C/geoloc%3E%20%3C/geolocs%3E%20%3Csearchradius%3E100%3C/searchradius%3E%20%3Cradiusuom%3Emile%3C/radiusuom%3E%20%3C/formdata%3E%20%3C/request%3E",
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
        location_type = "fossil"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        raw_address = ""
        hours_of_operation = "<MISSING>"

        # print("data ==== "+str(soup))

        for script in soup.find_all("poi"):

            location_name = script.find('name').text
            street_address = script.find('address1').text + " " + script.find('address2').text
            city = script.find('city').text
            state = script.find('state').text
            zipp = script.find('postalcode').text
            country_code = script.find('country').text
            latitude = script.find('latitude').text
            longitude = script.find('longitude').text
            phone = script.find('phone').text.replace('&#xa0;',"")

            if len(location_name) == 0:
                location_name = "<MISSING>"

            if len(street_address) == 0:
                street_address = "<MISSING>"

            if len(city) == 0:
                city = "<MISSING>"

            if len(state) == 0:
                state = "<MISSING>"

            if len(zipp) == 0:
                zipp = "<MISSING>"

            if len(country_code) == 0:
                country_code = "US"

            if len(latitude) == 0:
                latitude = "<MISSING>"

            if len(longitude) == 0:
                longitude = "<MISSING>"

            if len(phone) == 0:
                phone = "<MISSING>"

            if len(script.find('sundayopen').text) > 0 or len(script.find('mondayopen').text) > 0 \
                    or len(script.find('tuesdayopen').text) > 0 or len(script.find('wednesdayopen').text) > 0 \
                    or len(script.find('thursdayopen').text) > 0 or len(script.find('fridayopen').text) > 0 \
                    or len(script.find('saturdayopen').text) > 0:
                hours_of_operation = "Sunday = " + script.find('sundayopen').text + " - " + script.find(
                    'sundayclose').text + ", " + \
                                     "Monday = " + script.find('mondayopen').text + " - " + script.find(
                    'mondayclose').text + ", " + \
                                     "Tuesday = " + script.find('tuesdayopen').text + " - " + script.find(
                    'tuesdayclose').text + ", " + \
                                     "Wednesday = " + script.find('wednesdayopen').text + " - " + script.find(
                    'wednesdayclose').text + ", " + \
                                     "Thursday = " + script.find('thursdayopen').text + " - " + script.find(
                    'thursdayclose').text + ", " + \
                                     "Friday = " + script.find('fridayopen').text + " - " + script.find(
                    'fridayclose').text + ", " + \
                                     "Saturday = " + script.find('saturdayopen').text + " - " + script.find(
                    'saturdayclose').text
            else:
                hours_of_operation = "<MISSING>"

            # print("address_list === "+str(hours_of_operation))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if store[2] in addresses:
                continue

            addresses.append(store[2])

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
