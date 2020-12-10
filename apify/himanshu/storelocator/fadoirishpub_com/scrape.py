import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fadoirishpub_com')


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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    # logger.info("soup ===  first")
    base_url = "https://fadoirishpub.com"
    r = session.get("https://fadoirishpub.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""
    for script in soup.find_all('div', {'class': 'location-content'}):
        list_store_detail = list(script.stripped_strings)
        if "Abu Dhabi" in list_store_detail:
            continue
        if 'Go To Pub' in list_store_detail:
            list_store_detail.remove('Go To Pub')
        location_name = list_store_detail[0]
        street_address = list_store_detail[-3].replace("Denver",'2199-2001 Blake St')
        city = list_store_detail[-2].split(',')[0].replace("Blake Street & 22nd Street",'Denver')
        state = list_store_detail[-2].split(',')[-1].replace("Blake Street & 22nd Street",' CO 80205').split(" ")[1]
        zipp = list_store_detail[-2].split(',')[-1].replace("Blake Street & 22nd Street",' CO 80205').split(" ")[-1]
        store_url = script.find('a')['href']
        r_store = session.get(store_url, headers=headers)
        soup_store = BeautifulSoup(r_store.text, "lxml")
        try:
            longitude =soup_store.find("iframe",{"src":re.compile("https://www.google.com/maps/embed?")})['src'].split("!2d")[-1].split("!3d")[0]
            latitude =soup_store.find("iframe",{"src":re.compile("https://www.google.com/maps/embed?")})['src'].split("!2d")[-1].split("!3d")[1].split("!2m")[0]
        except:
            latitude=''
            longitude=''
        try:
            phone = soup_store.find("a",{"href":re.compile("tel")})['href'].replace("tel:",'')
        except:
            phone ="<MISSING>"
        try:
            hours_of_operation = (" ".join((list(soup_store.find('div',{'class':'info-box'}).stripped_strings))[1:]).replace("New Hours of Operation Coming Soon","<MISSING>").replace("WE ARE CURRENTLY CLOSED DUE TO STATE MANDATE.",'').replace("Scheduled to reopen July 7",'').replace("( Click for kitchen hours )",'').replace(" – "," - "))
            # hours_of_operation = " ".join(list(soup_store.find('div',{'class':'info-box'}).stripped_strings)).replace("Hours",'').replace("New  of Operation Coming Soon","<MISSING>").replace("WE ARE CURRENTLY CLOSED DUE TO STATE MANDATE.",'').replace("Scheduled to reopen July 7",'').strip().replace("( Click for kitchen hours )",'')
        except:
            hours_of_operation = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,store_url]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if "20001" in zipp:
            continue
        yield store
        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
