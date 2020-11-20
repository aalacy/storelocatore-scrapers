import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('costcutters_com')
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.signaturestyle.com"
    addressess = []
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }
    r = session.get("https://www.signaturestyle.com/salon-directory.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a",{"class","btn btn-primary"})
    for link in links:
        if "/locations/pr.html" in link['href']:
            continue
        r1 = session.get(base_url+link['href'], headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        locations = soup1.find_all("tr")
        for location in locations:
            if "https" not in location.find("a")['href']:
                page_url = base_url+location.find("a")['href']
            else:
                page_url = location.find("a")['href']

            r3 = session.get(page_url, headers=headers)
            soup3 = BeautifulSoup(r3.text, "lxml")
            if soup3.find("h2",{"class":"hidden-xs salontitle_salonlrgtxt"}):
                location_name = soup3.find("h2",{"class":"hidden-xs salontitle_salonlrgtxt"}).text.strip()
            else:
                continue
            street_address = soup3.find("span",{"itemprop":"streetAddress"}).text.strip()
            city = soup3.find("span",{"itemprop":"addressLocality"}).text.strip()
            state = soup3.find("span",{"itemprop":"addressRegion"}).text.strip()
            zipp = soup3.find("span",{"itemprop":"postalCode"}).text.strip()
            if len(zipp) == 5:
                country_code = "US"
            else:
                country_code = "CA"
            store_number = page_url.split("-")[-1].replace(".html","").strip()
            phone = soup3.find("a",{"id":"sdp-phone"}).text.strip()
            location_type = "Salons"
            latitude = soup3.find("meta", {"itemprop":"latitude"})['content']
            longitude = soup3.find("meta", {"itemprop":"longitude"})['content']
            try:
                hours_of_operation = " ".join(list(soup3.find("div",{"class":"salon-timings"}).stripped_strings))
            except:
                hours_of_operation = " ".join(list(soup3.find("section",{"class":"col-sm-12 col-md-5 col-block"}).stripped_strings))
            if "/cost-cutters" not in page_url:
                continue
            store=[]
            store.append("https://www.costcutters.com")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url)
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
