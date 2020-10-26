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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    base_url = "https://www.thefreshgrocer.com"

    zip_code = '08311'
    r = session.post("https://shop.thefreshgrocer.com/StoreLocatorSearch",
                      headers=headers,
                      data='Region=&SearchTerm=' + str(zip_code) + '&Radius=1000&Take=9999&Redirect=')
    soup = BeautifulSoup(r.text, "lxml")

    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    for script in soup.find_all('li', {'class': 'stores__store'}):
        list_address = list(script.find('div', {'class': 'store__address'}).stripped_strings)
        list_hours = list(script.find('div', {'class': 'info__hoursAndServices'}).stripped_strings)

        if list_address[0] in addresses:
            continue

        addresses.append(list_address[0])

        map_url = script.find('div', {'class': 'store__controls'}).find('a')['href']
        # print('Map Url ===== ' + str(map_url))
        # print(str(len(addresses)) + ' == list_address ===== ' + str(list_address))
        # print('list_hours ===== ' + str(list_hours))
        # print('Distance ===== ' + str(script.find('span',{'class':'store__distance'}).text))

        street_address = list_address[0]
        phone = list_address[-1]
        city = list_address[1].split(',')[0]
        state = list_address[1].split(',')[-1].strip().split(' ')[0]
        zipp = list_address[1].split(',')[-1].strip().split(' ')[1]
        hours_of_operation = ', '.join(list_hours).replace("–","-")
        location_name = city
        latitude = map_url.split('?daddr=')[1].split(',')[0]
        longitude = map_url.split('?daddr=')[1].split(',')[1]

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
