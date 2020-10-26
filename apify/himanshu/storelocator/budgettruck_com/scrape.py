import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('budgettruck_com')




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
    return_main_object = []
    addressess = []

    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.budgettruck.com/"
    r = session.get("https://www.budgettruck.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")

    for ul in soup.find_all("ul",{"class":"bt-lp-list-group"}):
        for li in ul.find_all("li"):
            location = "https://www.budgettruck.com/" + li.find("a")["href"]
            location_request = session.get(location)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            city_data_raw = location_soup.find_all("div",{"class":"row bt-locations-city-ls bt-default-well"})
            for city in city_data_raw:
                city_link = "https://www.budgettruck.com/locations/" + city.find("a")["href"]
                city_request = session.get(city_link)
                city_soup = BeautifulSoup(city_request.text,"lxml")
                script = city_soup.find(lambda tag: (tag.name == "script") and 'locationJSON' in tag.text).text
                json_data = json.loads(script.split("var locationJSON = '")[1].split("var locationArray")[0].replace("';",""))

                for dealer in json_data:
                    locator_domain = base_url
                    location_name = dealer['DealerName']
                    if dealer['Address2'] != None:
                        street_address = dealer['Address'] + ", " + dealer['Address2']
                    else:
                        street_address = dealer['Address']

                    city = dealer['City']
                    state = dealer['State']
                    zipp = dealer['Zip']
                    country_code = "US"
                    
                    store_number = dealer['DealerNumber']
                    phone = dealer['Phone']
                    location_type = 'Truck Rental'
                    latitude = dealer['Latitude']
                    longitude = dealer['Longitude']
                    hoo = []
                    for hours in dealer['DealerOperations']:
                        days = hours['Days']
                        time = hours['Time']
                        frame = days + " " +time
                        hoo.append(frame)
                    hours_of_operation = ','.join(hoo)
                    page_url = "https://www.budgettruck.com/locations/" + state.lower() + "/" + city.lower().replace("-"," ") + "/" + str(store_number)
                    logger.info(page_url)
                    store = []
                    store.append(locator_domain)
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
                    store.append(hours_of_operation)
                    store.append(page_url)
            

                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    yield store
                            


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
