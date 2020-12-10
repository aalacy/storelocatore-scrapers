import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
# import re
# import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cafedavignon_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8",newline ="") as output_file:
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
    addresses=[]
    base_url = locator_domain="https://www.cafedavignon.com"
    r = session.get("https://www.cafedavignon.com/locations/#section-new-york/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for sec in soup.find_all("section",class_="content container"):
        for li in sec.find_all("li",class_="card"):
            page_url ="https://www.cafedavignon.com"+ li.find("a",class_="card__btn")["href"]
            if "coming-soon" not in page_url:
                location_name = li.find("h3",class_="card__heading").text.strip()
                r1 = session.get(page_url,headers=headers)
                soup1 = BeautifulSoup(r1.text,"lxml")
                section = soup1.find("section",{"id":"intro"})
                address = list(soup1.find("a",{"data-bb-track-category":"Address"}).stripped_strings)
                street_address = " ".join(address[:-1]).strip()
                city= address[-1].split(",")[0].strip()
                state =address[-1].split(",")[-1].split()[0].strip()
                zipp = address[-1].split(",")[-1].split()[-1].strip() 
                country_code = "US"
                location_type="<MISSING>"
                store_number = "<MISSING>"
                phone = soup1.find("a",{"data-bb-track-category":"Phone Number"}).text.strip()
                latitude = soup1.find("div",class_="gmaps")["data-gmaps-lat"]
                longitude = soup1.find("div",class_="gmaps")["data-gmaps-lng"]
                hours_list = []
                for hours in soup1.find("section",{"id":"intro"}).find("a",{"data-bb-track-category":"Phone Number"}).find_all_next("p"):

                    if "Sunday" in hours.text or "Monday" in hours.text:
                        hours_list.append(hours.text)
                if hours_list:
                    hours_of_operation = " ".join(hours_list)
                else:
                    hours_of_operation = "<MISSING>"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(store[2]+ " "+store[-1]) not in addresses and country_code:
                    addresses.append(str(store[2]+ " "+store[-1]))

                    store = [str(x).strip() if x else "<MISSING>" for x in store]

                    # logger.info("data = " + str(store))
                    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
