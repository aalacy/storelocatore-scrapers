
import csv
import re
import pdb
import requests
from lxml import etree
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sharkeyscutsforkids_com')



base_urls = 'https://sharkeyscutsforkids.com/'



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess=[]
    url =[]
    base_url = "https://sharkeyscutsforkids.com/locations/"
    soup1 = bs(requests.get(base_url).text,'lxml')
    for q in soup1.find_all("h2",class_="geodir-entry-title"):
        page_url =q.find("a")['href']
        name =q.find("a").text.strip()
        # logger.info(page_url)
        soup1 = bs(requests.get(q.find("a")['href']).text,'lxml')
        address = soup1.find("span",{"itemprop":"streetAddress"}).text.strip().replace(",",'')
        try:
            address1 = soup1.find("span",{"itemprop":"addressNeighbourhood"}).text.strip().replace(",",'')
        except:
            address1=''
        street_address = address+ ' '+address1
        city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip().replace(",",'')
        state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip().replace(",",'')
        try:
            zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip().replace(",",'')
        except:
            zipp="<MISSING>"
        address = soup1.find("span",{"itemprop":"streetAddress"}).text.strip().replace(",",'')
        try:
            phone = soup1.find("div",{"class":"geodir-i-contact","class":"geodir_contact"}).text.replace("Phone:",'').strip()
        except:
            phone="<MISSING>"
        # logger.info( phone)
        hours_of_operation="<MISSING>"
        try:
            hours_of_operation = " ".join(list(soup1.find("div",{"class":"geodir_timing"}).stripped_strings)).replace("Business Hours: ",'').replace("|",'')
        except:
            pass
        try:
            latitude=(json.loads(soup1.find("script",{"type":"application/ld+json"}).text)['geo']['latitude'])
        except:
            latitude='<MISSING>'
        try:
            longitude=(json.loads(soup1.find("script",{"type":"application/ld+json"}).text)['geo']['longitude'])
        except:
            longitude='<MISSING>'
        store = []
        code="US"
        if  "759 Pembina Hwy" in street_address:
            code="CA"
        store.append(base_urls)
        store.append(name.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(zipp)
        store.append(code)
        store.append("<MISSING>")
        store.append( phone.replace(" (4FUN)",'').replace("CUTS (2887)",'2887').replace("(CUTS)",''))
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>" )
        store.append(longitude if longitude else "<MISSING>")
        store.append( hours_of_operation)
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        # store = [x.replace("–", "-") if type(x) ==
        #          str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode(
            'ascii').strip() if type(x) == str else x for x in store]
        if "8 Topsfield Rd" in store or "Sderot Rothschild 9" in store:
            pass
        else:
            # logger.info("data ===" + str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
