import csv
from lxml import etree
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import time
from random import randint
from unidecode import unidecode
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('stellabarra_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def sanitize(x):
    return unidecode(x)

def fetch_data():
    data = []
    url = "https://www.stellabarra.com"
    session = SgRequests()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//a[@class="underline tracked"]/@href')

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    for store_link in store_list:

        req = session.get(store_link, headers = HEADERS)
        time.sleep(randint(1,2))

        item = BeautifulSoup(req.text,"lxml")

        locator_domain = "stellabarra.com"
        location_name = "Stella Barra " + item.find('h1').text.strip()
        logger.info(location_name)

        raw_address = item.find("footer").div.find_all("div")[3].a.text.replace("\r\n",",").split(",")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip()
        if " " in state:
            zip_code = state.split()[1].strip()
            state = state.split()[0].strip()
        else:
            zip_code = "<MISSING>"

        country_code = "US"

        store_number = "<MISSING>"
        try:
            phone = item.find('a', attrs={'data-label': 'Call'}).text.strip()
        except:
            phone = "<MISSING>"

        location_type = "<MISSING>"
        try:
            raw_gps = item.find('a', attrs={'data-label': 'Map'})["href"]
            lat_pos = raw_gps.find("@")+1
            latitude = raw_gps[lat_pos:raw_gps.find(",", lat_pos)].strip()
            long_pos = raw_gps.find(",", lat_pos)
            longitude = raw_gps[long_pos+1:raw_gps.find(",",long_pos+3)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        raw_hours = item.find("footer").div.find_all("div")[2].text
        raw_hours = raw_hours[raw_hours.find("\r\n"):raw_hours.rfind("\n\r")].strip()
        if "Dine-In" in raw_hours or "Friday" in raw_hours[:15]:
            raw_hours = item.find("footer").div.find_all("div")[2].text
            raw_hours = raw_hours[raw_hours.find("Monday"):raw_hours.rfind("\n")].strip()

        hours_of_operation = sanitize(raw_hours).replace("\r\n"," ").replace("\r\n"," ").replace("\xa0"," ").replace("\n"," ").strip()
        if "Brunch" in hours_of_operation:
            hours_of_operation = hours_of_operation[:hours_of_operation.find("Brunch")-2].strip()

        data.append([locator_domain, store_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
