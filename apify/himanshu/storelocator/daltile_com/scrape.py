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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }

    base_url = "https://www.daltile.com"

    r_appkey = requests.get(
        'https://hosted.where2getit.com/daltile/store-locator19.html?addressline=11576&searchradius=25%7C50%7C100%7C250&premierstatementsdealer=1&geoip=1',
        headers=headers)
    soup_appkey = BeautifulSoup(r_appkey.text, "lxml")

    app_key = soup_appkey.text.split("appkey: '")[1].split("'")[0]

    #print("r_appKey === " + str(app_key))

    for zip_code in zips:
        #print(zip_code)

        # zip_code = 99655
        r = requests.post("https://hosted.where2getit.com/daltile/rest/locatorsearch",
                          headers=headers,
                          data='{"request":{"appkey":"085E99FA-1901-11E4-966B-82C955A65BB0","formdata":{'
                               '"dynamicSearch":true,"geoip":false,"dataview":"store_default","limit":1000,'
                               '"geolocs":{"geoloc":[{"addressline":"' + str(zip_code) + '","country":"","latitude":"",'
                                                                                         '"longitude":""}]},"searchradius":"100"}}}')
        json_data = r.json()

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
        location_type = "daltile"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        raw_address = ""
        hours_of_operation = "<MISSING>"

        if 'collection' not in json_data['response']:
            continue
        # print(len(json_data['response']['collection']))
        for address_list in json_data['response']['collection']:

            # print('json data = ' + str(address_list))

            latitude = address_list['latitude']
            longitude = address_list['longitude']
            zipp = address_list['postalcode']
            location_name = address_list['name']
            city = address_list['city']
            country_code = address_list['country']
            state = address_list['state']
            street_address = address_list['address1']
            phone = address_list['phone']
            # print(address_list.keys())
            if street_address is not None:
                if address_list['address2'] is not None:
                    street_address += ", " + address_list['address2']
                soup_street_address = BeautifulSoup(street_address, "lxml")
                street_address = ", ".join(list(soup_street_address.stripped_strings))

            else:
                street_address = '<MISSING>'

            if location_name is None or len(location_name) == 0:
                location_name = "<MISSING>"

            if street_address is None or len(street_address) == 0:
                street_address = "<MISSING>"

            if city is None or len(city) == 0:
                city = "<MISSING>"

            if state is None or len(state) == 0:
                state = "<MISSING>"

            if zipp is None or len(zipp) == 0:
                zipp = "<MISSING>"
            else:
                if not any(char.isdigit() for char in zipp):
                    print("zipp === "+zipp)
                    zipp = "<MISSING>"

            # if country_code is None or len(country_code) == 0:
            if str(zipp[-5:]).isdigit():
                country_code = "US"
            else:
                country_code = "CA"

            if latitude is None or len(latitude) == 0:
                latitude = "<MISSING>"

            if longitude is None or len(longitude) == 0:
                longitude = "<MISSING>"

            if phone is None or len(phone) == 0:
                phone = "<MISSING>"

            is_missing_hours = True
            if address_list['sunday_open'] is not None and address_list['sunday_closed'] is not None:
                is_missing_hours = False
                hours_of_operation = "Sunday = " + address_list['sunday_open'] + " - " + address_list[
                    'sunday_closed'] + ", "
            else:
                hours_of_operation += "Sunday = CLOSED" + ", "

            if address_list['monday_open'] is not None and address_list['monday_closed'] is not None:
                is_missing_hours = False
                hours_of_operation += "Monday = " + address_list['monday_open'] + " - " + address_list[
                    'monday_closed'] + ", "
            else:
                hours_of_operation += "Monday = CLOSED" + ", "

            if address_list['tuesday_open'] is not None and address_list['tuesday_closed'] is not None:
                is_missing_hours = False
                hours_of_operation += "Tuesday = " + address_list['tuesday_open'] + " - " + address_list[
                    'tuesday_closed'] + ", "
            else:
                hours_of_operation += "Tuesday = CLOSED" + ", "

            if address_list['wednesday_open'] is not None and address_list['wednesday_closed'] is not None:
                is_missing_hours = False
                hours_of_operation += "Wednesday = " + address_list['wednesday_open'] + " - " + address_list[
                    'wednesday_closed'] + ", "
            else:
                hours_of_operation += "Wednesday = CLOSED" + ", "

            if address_list['thursday_open'] is not None and address_list['thursday_closed'] is not None:
                is_missing_hours = False
                hours_of_operation += "Thursday = " + address_list['thursday_open'] + " - " + address_list[
                    'thursday_closed'] + ", "
            else:
                hours_of_operation += "Thursday = CLOSED" + ", "

            if (address_list['friday_open'] is not None) and (address_list['friday_closed'] is not None):
                is_missing_hours = False
                hours_of_operation += "Friday = " + address_list['friday_open'] + " - " + address_list[
                    'friday_closed'] + ", "
            else:
                hours_of_operation += "Friday = CLOSED" + ", "

            if (address_list['saturday_open'] is not None) and (address_list['saturday_closed'] is not None):
                is_missing_hours = False
                hours_of_operation += "Saturday = " + address_list['saturday_open'] + " - " + address_list[
                    'saturday_closed']
            else:
                hours_of_operation += "Saturday = CLOSED"

            hours_of_operation = hours_of_operation.replace('CLOSED - CLOSED', 'CLOSED')

            if is_missing_hours:
                hours_of_operation = "<MISSING>"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if store[2] + store[-3] in addresses:
                continue

            addresses.append(store[2] + store[-3])

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
        # break
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
