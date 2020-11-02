import csv
import requests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('urgentteam_com')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    address = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    base_url = "https://www.urgentteam.com/"
    list1=['urgent-team','sherwood-urgent-care','physicians-care','baptist-health-urgent-care','washington-regional-urgent-care','huntsville-hospital-urgent-care']
    for q in range(1,7):
        # location_type =q.replace("-",' ')
        link = "https://www.urgentteam.com/locations/page/"+str(q)
        soup = bs(requests.get(link,headers=headers).text,'lxml')
        for dt in soup.find_all("li",{"class":"m-locations__item"}):
            full = list(dt.find("address",{"class":"m-location__address"}).stripped_strings)
            street_address = " ".join(full[:-1]).replace(",",'')
            city = full[-1].split(",")[0]
            state = full[-1].split(",")[-1].split(" ")[1]
            zipp = full[-1].split(",")[-1].split(" ")[2]
            hours_of_operation = " ".join(list(dt.find("div",{"class":"m-location__hours m-location-hours"}).stripped_strings))
            page_url = dt.find("a",{"class":"m-location__cta"})['href']
            location_name = " ".join(list(dt.find("a",{"class":"m-location__titles"}).stripped_strings))
            soup1 = bs(requests.get(page_url,headers=headers).text,'lxml')
            latitude = json.loads(soup1.find_all("script",{"type":"application/ld+json"})[-1].text)['geo']['latitude']
            longitude = json.loads(soup1.find_all("script",{"type":"application/ld+json"})[-1].text)['geo']['longitude']
            try:
                phone = soup1.find_all("a",{"class":"m-location-panel__phone"})[-1].text
            except:
                phone="<MISSING>"
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append( "US")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append( soup1.find("p",{"class":"o-breadcrumbs__text"}).text.split(",")[0])
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation.replace("N/A",'<MISSING>') if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            # logger.info("~~~~~~~~~~~~~~~~~ ",store)
            # if store[2] in addressesss :
            #     continue
            # addressesss.append(store[2])
            yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
