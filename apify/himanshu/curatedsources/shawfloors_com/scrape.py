# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shawfloors_com')




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
    return_main_object = []
    addresses = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    link = "https://shawfloors.com/stores/storelist"
    r = requests.get(link, headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    a_tage = soup.find("ul",{"id":"dealerList"}).find_all("a")

    for i in a_tage:
        locator_domain = "https://shawfloors.com"
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        # country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        sub_l = "https://shawfloors.com"
        # logger.info(sub_l+i['href'])

        page_url = sub_l+i['href']
        try:
            r1 = requests.get(sub_l+i['href'], headers=headers)
            soup1= BeautifulSoup(r1.text,"lxml")
        except:
            continue
        street_address = " ".join(list(soup1.find("span",{"itemprop":"streetAddress"}).stripped_strings))
        city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
        state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
        location_name = soup1.find("span",{"itemprop":"name"}).text.strip()
        

        zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip().lstrip()
        if len(zipp)==6 or len(zipp)==7:
            country_code = "CA"
        else:
            country_code = "US"

        phone = soup1.find("a",{"id":"p_lt_ctl02_pageplaceholder_p_lt_ctl01_RetailerProfile_PhoneLink"}).text.strip()
        hours1 = soup1.find("div",{"class":"hours"})
        if hours1 != None:
            hours_of_operation = (" ".join(list(hours1.stripped_strings)).replace("|"," ").replace("Hours","").replace("    ",""))
        else:
            hours_of_operation = "<MISSING>"

    
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    str(store_number), str(phone), location_type, str(latitude), str(longitude), hours_of_operation,page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
