

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('guessbymarciano_guess_ca')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    base_url = "https://guessbymarciano.guess.ca/"


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    location_url = "https://stores.guessbymarciano.guess.ca/"

    all_soup = bs(session.get(location_url,headers=headers).content,"lxml")

    for a_link in all_soup.find("div",{"id":"browse-expand"}).find_all("a",{"data-ga":re.compile("Maplist, Region -")}):

        city_soup = bs(session.get(a_link['href']).content, "lxml")

        for city_link in city_soup.find_all("a",{"title":re.compile("Stores in")}):

            store_soup = bs(session.get(city_link['href']).content, "lxml")

            for url in store_soup.find_all("a",{"title":re.compile("#")}):
                
                page_url = url['href']
                #logger.info(page_url)
                if session.get(page_url).status_code != 200:
                    continue
                location_soup = bs(session.get(page_url).content, "lxml")
                
                data = json.loads(location_soup.find(lambda tag:(tag.name == "script") and "RLS.defaultData" in tag.text).text.split(">")[1].split("<")[0].replace("\\",""))
                
                location_name = data['location_name']+" "+ data['location_shopping_center']
                street_address = (data['address_1']+" "+ data['address_2']).strip()
                city = data['city']
                state = data['region']
                zipp = data['post_code']
                country_code = data['country']
                store_number = data['fid']
                if data['store_type_cs']:
                    location_type = data['store_type_cs']
                else:
                    location_type = location_name
                lat = data['lat']
                lng = data['lng']
                phone = location_soup.find("a",{"title":"Call Store"}).text
                hours = " ".join(list(location_soup.find("div",{"class":"hours"}).stripped_strings))
        
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)
                if store[2] in addressess:
                    continue
                addressess.append(store[2])

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                
                yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
