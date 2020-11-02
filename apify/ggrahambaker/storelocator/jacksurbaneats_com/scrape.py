import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from random import randint
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jacksurbaneats_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    
    base_link = "https://www.jacksurbaneats.com/locations/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    locator_domain = 'jacksurbaneats.com'
    locs = base.find_all(class_="et_pb_text_inner")[1:-1]
    all_store_data = []
    for loc in locs:
        raw_data = str(loc.p).split("<br/>")
        location_name = loc.h1.text
        
        try:
            street_address = loc.a.text.strip()
        except:
            continue
        logger.info(location_name)
        city, state, zip_code = addy_ext(raw_data[-1][:-4].replace("\n","").replace("\xa0", " "))
        phone_number = raw_data[-2].strip()

        hours = loc.find_all("p")[1].text.replace("pm", "pm ").replace("\n","").strip()
        if hours == ".":
            phone_number = "<MISSING>"
            hours = loc.find_all("p")[-1].text.replace("pm", "pm ").replace("\n","").strip()
        if "(" in hours:
            phone_number = hours
            hours = loc.find_all("p")[2].text.replace("pm", "pm ").replace("\n","").strip()
            
        link = loc.find('a')['href']

        coords = link[link.find('/@') + 2:link.find('z/d')].split(',')

        if 'google' in coords[0]:
            req = session.get(link, headers = headers)
            time.sleep(randint(1,2))
            try:
                maps = BeautifulSoup(req.text,"lxml")
            except (BaseException):
                logger.info('[!] Error Occured. ')
                logger.info('[?] Check whether system is Online.')

            try:
                raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
                latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
                longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
        else:
            latitude = coords[0]
            longitude = coords[1]

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, latitude, longitude, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
