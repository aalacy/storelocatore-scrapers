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
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*'
    }


    addresses = []
    base_url = "http://checksmartstores.com"

    r = session.post("https://www.ccfi.com/ajax/stores.php", headers=headers,data='zip=11756&distance=all')
    json_data = r.json()

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""

    for location in json_data["stores"]:
        # print("location ==== " + str(location))

        store_number = location["storeNumber"]
        city = location["city"]
        state = location["state"]
        zipp = location["zip"]
        latitude = location["lat"]
        longitude = location["lng"]
        phone = location["phone"]
        street_address = location["street"]
        location_name = city

        if latitude == "0":
            latitude = ""
        if longitude == "0":
            longitude = ""

        if location["sunday_open"] == "Closed":
            hours_of_operation = "Sunday "+ location["sunday_open"] +" "
        else:
            hours_of_operation = "Sunday "+ location["sunday_open"] +" - "+ location["sunday_close"]+" "

        if location["monday_open"] == "Closed":
            hours_of_operation += "Monday "+ location["monday_open"]+" "
        else:
            hours_of_operation += "Monday "+ location["monday_open"] +" - "+ location["monday_close"]+" "

        if location["tuesday_open"] == "Closed":
            hours_of_operation += "Tuesday "+ location["tuesday_open"]+" "
        else:
            hours_of_operation += "Tuesday "+ location["tuesday_open"] +" - "+ location["tuesday_close"]+" "

        if location["wednesday_open"] == "Closed":
            hours_of_operation += "Wednesday "+ location["wednesday_open"]+" "
        else:
            hours_of_operation += "Wednesday "+ location["wednesday_open"] +" - "+ location["wednesday_close"]+" "

        if location["thursday_open"] == "Closed":
            hours_of_operation += "Thursday "+ location["thursday_open"]+" "
        else:
            hours_of_operation += "Thursday "+ location["thursday_open"] +" - "+ location["thursday_close"]+" "

        if location["friday_open"] == "Closed":
            hours_of_operation += "Friday "+ location["friday_open"]+" "
        else:
            hours_of_operation += "Friday "+ location["friday_open"] +" - "+ location["friday_close"]+" "

        if location["saturday_open"] == "Closed":
            hours_of_operation += "Saturday "+ location["saturday_open"]+" "
        else:
            hours_of_operation += "Saturday "+ location["saturday_open"] +" - "+ location["saturday_close"]+" "

        # print("hours_of_operation === "+ str(hours_of_operation))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
