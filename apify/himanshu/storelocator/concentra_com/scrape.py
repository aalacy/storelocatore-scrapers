import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import phonenumbers
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('concentra_com')



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
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    # }
    base_url = "https://www.concentra.com"

    r = session.get("https://www.concentra.com//sxa/search/results/?s={449ED3CA-26F3-4E6A-BF21-9808B60D936F}|{449ED3CA-26F3-4E6A-BF21-9808B60D936F}&itemid={739CBD3C-A3B6-4CA2-8004-BF6005BB28E9}&v={D907A7FD-050F-4644-92DC-267C1FDE200C}&p=1000").json()
    for data in r['Results']:
        page_url = base_url+data['Url']
        # logger.info(page_url)
        location_r = session.get(page_url)
        soup = BeautifulSoup(location_r.text, "lxml")
        try:
            location_name = soup.find("h1",{"class":"field-centername"}).text.strip()
            location_type = location_name.split("-")[-1].strip()
        except:
            location_name = "<MISSING>"
            location_type = "<MISSING>"
        street_address = " ".join(list(soup.find("div",{"itemprop":"address"}).stripped_strings)[:-5])
        city = soup.find("span",{"itemprop":"addressLocality"}).text.strip()
        state = soup.find("span",{"itemprop":"addressRegion"}).text.strip()
        zipp = soup.find("span",{"itemprop":"postalCode"}).text.strip()
        phone = phonenumbers.format_number(phonenumbers.parse(soup.find("span",{"itemprop":"telephone"})['content'], 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        latitude = soup.find("meta",{"itemprop":"latitude"})['content']
        longitude = soup.find("meta",{"itemprop":"longitude"})['content']
        hours = " ".join(list(soup.find("div",{"class":"hours-container"}).stripped_strings)).replace("Hours","").strip()

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        # logger.info("data ==="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
