import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('iwc_com')





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


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': 'application/json'
    }

    # logger.info("soup ===  first")
    addresses = []
    base_url = "https://www.iwc.com"

    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

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
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = "<MISSING>"

    # logger.info("soup ==== " + str(soup))

    total_result = 0
    page_result = 0
    current_offset = 0
    isFinish = False

    while isFinish is False:
        r = session.get("https://stores.iwc.com/search?country=US&offset=" + str(current_offset), headers=headers)
        json_data = r.json()

        page_result = len(json_data["response"]["entities"])
        current_offset += page_result


        # logger.info("json_data === " + str(json_data["response"]["count"]))
        # logger.info("entities === " + str(page_result))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        for location in json_data["response"]["entities"]:

            street_address = str(location["profile"]["address"]["line1"]) +" "+ str(location["profile"]["address"]["line2"]) +" "+ str(location["profile"]["address"]["line3"])
            street_address =  street_address.replace(" None","")
            location_name = location["profile"]["name"].replace('&','and')
            state = location["profile"]["address"]["region"]
            city = location["profile"]["address"]["city"]
            zipp = location["profile"]["address"]["postalCode"]
            country_code = location["profile"]["address"]["countryCode"]
            phone = location["profile"]["mainPhone"]["display"]

            # if "displayCoordinate" in location["profile"]:
            try:
                latitude = location["profile"]["displayCoordinate"]["lat"]
                longitude = location["profile"]["displayCoordinate"]["long"]
            except:
                # logger.info("https://stores.iwc.com/search?country=US&offset=" + str(current_offset))
                latitude = location['profile']['yextDisplayCoordinate']['lat']
                longitude = location['profile']['yextDisplayCoordinate']['long']

            hours_of_operation = ""
            if "hours" in location["profile"]:
                for days_hours in location["profile"]["hours"]["normalHours"]:
                    # logger.info("days_hours === "+ str(days_hours))

                    if days_hours["isClosed"] is False:
                        hours_of_operation += days_hours["day"] +" " +  str(days_hours["intervals"][0]["start"]/100).replace(".",":") + "0 - "+ str(days_hours["intervals"][0]["end"]/100).replace(".",":")+"0"
                    else:
                        hours_of_operation += days_hours["day"] +" Closed"

                    hours_of_operation += " "
            hours_of_operation = hours_of_operation.capitalize()




            # logger.info("s === "+ str(latitude))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x if x else "<MISSING>" for x in store]
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.strip() if type(x) == str else x for x in store]
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        if page_result == 0:
            isFinish = True


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
