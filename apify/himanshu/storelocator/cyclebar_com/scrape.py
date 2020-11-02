import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cyclebar_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://members.cyclebar.com/api/brands/cyclebar/locations?open_status=external&geoip="
    r_locations = session.get(base_url, headers=headers).json()
    json_data = r_locations['locations']
    for location in json_data:
        coming_soon = location['coming_soon']
        if str(coming_soon) == "True":
            pass
        else:
            location_name = location['name']
            address2 = location['address2']
            street_address = location['address'] + \
                " " + str(address2).replace('None', '')
            city = location['city']
            state = location['state']
            zipp = location['zip']
            country_code = location['country_code']
            phone = location['phone']
            latitude = location['lat']
            longitude = location['lng']
            location_url = location['site_url']
            if location_url != None:
                r = session.get(location_url, headers=headers)
                soup = BeautifulSoup(r.text, "lxml")
                hours = soup.find("span", {"class": "location-info-map__info"})
                if hours != None:
                    try:
                        hours1 = soup.find(
                            "i", {"class": "location-info-map__icon"}).find_next('span')['data-hours']
                        json_data1 = json.loads(hours1)
                        hours_of_operation = ''
                        for data in json_data1:

                            if len(json_data1[data]) == 1:
                                hours_of = data, json_data1[data][0][0], json_data1[data][0][1]
                                d = datetime.strptime(hours_of[1], "%H:%M")
                                t = d.strftime("%I:%M %p")
                                d1 = datetime.strptime(hours_of[2], "%H:%M")
                                t1 = d1.strftime("%I:%M %p")
                                hours_of_operation = hours_of_operation + \
                                    ' ' + hours_of[0] + ' ' + t + ' ' + t1
                            else:
                                hours_of = data, json_data1[data][0][0], json_data1[data][
                                    0][1], json_data1[data][1][0], json_data1[data][1][1]
                                d2 = datetime.strptime(hours_of[1], "%H:%M")
                                t2 = d2.strftime("%I:%M %p")
                                d3 = datetime.strptime(hours_of[2], "%H:%M")
                                t3 = d3.strftime("%I:%M %p")
                                d4 = datetime.strptime(hours_of[3], "%H:%M")
                                t4 = d4.strftime("%I:%M %p")
                                d5 = datetime.strptime(hours_of[4], "%H:%M")
                                t5 = d5.strftime("%I:%M %p")
                                hours_of_operation = hours_of_operation + ' ' + \
                                    hours_of[0] + ' ' + t2 + ' ' + \
                                    t3 + ' ' + t4 + ' ' + t5
                    except:
                        hours_of_operation = "<MISSING>"
            else:
                hours_of_operation = "<MISSING>"
            store = []
            store.append("https://www.cyclebar.com")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(
                hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(location_url)
            #logger.info("data ==" + str(store))
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
