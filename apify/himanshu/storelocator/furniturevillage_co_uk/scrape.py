
import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('furniturevillage_co_uk')



session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://www.furniturevillage.co.uk"
    r =  session.get("https://www.furniturevillage.co.uk/stores/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml") 
    for link in soup.find("div",{"class":"col-xs-12 select-store no-pd"}).find_all("option"):
        if link['value'] == "":
            continue
        page_url = base_url+link['value']
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            try:
                location_name = soup1.find("h1",{"class":"col-xs-12 center-xs"}).text.strip()
            except:
                location_name = soup1.find_all("div",{"class":"col-xs-12 center-xs"})[2].find("h1").text.strip()

            street_address = soup1.find("span",{"itemprop":"streetAddress"}).text
            city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
            state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
            zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip()
            phone = soup1.find("meta",{"itemprop":"telephone"})['content']
            latitude = soup1.find("meta",{"itemprop":"latitude"})['content']
            longitude = soup1.find("meta",{"itemprop":"longitude"})['content']
            hours = ''
            for time in soup1.find_all("p",{"itemprop":"openingHours"}):
                hours+= re.sub(r'\s+'," "," ".join(list(time.stripped_strings)))+" "
            hours_of_operation = hours
        except:
            continue 


        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state if state else "<MISSING>")
        store.append(zipp)
        store.append("UK")
        store.append("<MISSING>")
        store.append(phone )
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info("data===="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
