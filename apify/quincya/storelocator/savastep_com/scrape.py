import requests
from bs4 import BeautifulSoup
import csv
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('savastep_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_link = "http://savastep.com/locations.html"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    req = requests.get(base_link, headers=headers)

    try:
        base = BeautifulSoup(req.text,"lxml")
        logger.info("Got page")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    rows = base.findAll('span', attrs={'style': 'font-size: medium;'})

    data = []
    new_set = False
    data_num = 1
    for row_num in range(0,len(rows)):
        if new_set:
            new_set = False
            continue
        row_data = rows[row_num].text.strip()
        logger.info(row_data)
        locator_domain = "savastep.com"
        if "corner of" in row_data:
            continue
        if data_num == 1:
            location_name = row_data
            store_number = row_data[1:3]
            data_num = data_num + 1
        elif data_num == 2:
            street_address = row_data
            data_num = data_num + 1
        elif data_num == 3:
            city = row_data[:row_data.find(',')]
            state  = row_data[row_data.find(',')+1:row_data.find(',')+4].strip()
            zip_code = row_data[row_data.find(',')+5:].strip()
            if zip_code == "":
                zip_code = "<MISSING>"
            data_num = data_num + 1
        elif data_num == 4:
            phone = row_data
            country_code = "US"
            location_type = "<INACCESSIBLE>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
            data.append([locator_domain, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
            data_num = 1
            new_set = True
            
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
