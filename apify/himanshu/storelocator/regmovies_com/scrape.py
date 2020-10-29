import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import http as http_
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('regmovies_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.regmovies.com"
    r = session.get("https://www.regmovies.com/static/en/us/theatre-list",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    addressess = []
    return_main_object = []
    for href in soup.find_all("a",{"class":"btn-link"}):
        try:
            r1 = session.get("https://www.regmovies.com/"+href['href'],headers=headers)
        except:
            pass
        # logger.info("https://www.regmovies.com/"+href['href'])
        soup1 = BeautifulSoup(r1.text,"lxml")
        store_data = soup1.find(lambda tag: tag.name == "cinema-structured-data")
        # logger.info("~~~~~~~~~~~~~~~~~~~~",store_data )
        if store_data == None:
            continue

        address = store_data['data-address'].replace("["," ").replace("]"," ")
            
        # logger.info(store_data['data-telephone'])
        # location_list = json.loads(script.text.split("apiSitesList = ")[1].split("}}]")[0] + "}}]")
        # phone_request = session.get("https://www.regmovies.com" + location_list[0]["uri"],headers=headers)
        # phone_soup = BeautifulSoup(phone_request.text,"lxml")
        # phone = phone_soup.find("cinema-structured-data")["data-telephone"]
        # for store_data in location_list:
        #     address = store_data["address"]["address1"]
        #     if store_data["address"]["address2"] != None:
        #         address = address + " " + store_data["address"]["address2"]
        #     if store_data["address"]["address3"] != None:
        #         address = address + " " + store_data["address"]["address3"]
        #     if store_data["address"]["address4"] != None:
        #         address = address + " " + store_data["address"]["address4"]
        store = []
        store.append("https://www.regmovies.com")
        store.append(store_data['data-name'])
        store.append(address)
        store.append(store_data['data-city'])
        store.append(store_data['data-province'])
        store.append(store_data['data-postalcode'])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data['data-telephone'])
        store.append("<MISSING>")
        store.append(store_data["data-lat"])
        store.append(store_data["data-lon"])
        store.append("<MISSING>")
        store.append("https://www.regmovies.com/"+href['href'])
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        #logger.info(store)
        yield store
       

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
