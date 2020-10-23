import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('iflyworld_com')



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

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    locator_domain = 'https://www.iflyworld.com/'
    ext = 'find-a-location/'

    req = session.get(locator_domain + ext, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    main = base.find(class_="wrap usa")
    a_tags = main.find_all(class_="loc")

    link_list = [locator_domain[:-1] + a_tag['href'] for a_tag in a_tags]
    link_list.append("https://calgary.iflyworld.com/what-is-ifly/help-and-faqs")

    all_store_data = []
    for link in link_list:
        if link == "https://www.iflyworld.com":
            continue

        logger.info(link)
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        if "calgary" in link:
            
            location_name = "iFLY Calgary"

            cards = base.find_all(class_="card-body")
            for card in cards:
                if "Calgary, AB" in card.text:
                    break

            phone_number = re.findall("[[(\d)]{3}-[\d]{3}-[\d]{4}", str(card))[0]

            raw_address = card.text.split("\r\n\t")[2].strip().split(",")
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zip_code = '<MISSING>'
            hours = '<MISSING>'
            country_code = 'CA'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = "<MISSING>"
            longit = "<MISSING>"

        else:
            main = base.find(class_='info col')

            location_name = base.h2.text.strip()
            if "coming soon" in location_name.lower():
                continue
            phone_number = main.find(class_="tel").text.strip()

            hours = main.find(class_="sub-info hours").text.replace("HOURS","").replace("PM","PM ").replace("–","-").strip()
            hours = (re.sub(' +', ' ', hours)).strip()
            
            street_address = str(main.find(class_="sub-info contact").a).split('>')[1][:-4].strip()
            city, state, zip_code = addy_ext(str(main.find(class_="sub-info contact").a).split('>')[2][:-4].strip())

            country_code = 'US'
            store_number = '<MISSING>'
            location_type = ",".join(list(base.find(class_="programs col").ul.stripped_strings))
            if not location_type:
                location_type = '<MISSING>'

            map_link = main.find(class_="sub-info contact").a["href"]
            req = session.get(map_link, headers = HEADERS)
            maps = BeautifulSoup(req.text,"lxml")

            try:
                raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
                lat = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
                longit = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
            except:
                lat = "<MISSING>"
                longit = "<MISSING>"

        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
