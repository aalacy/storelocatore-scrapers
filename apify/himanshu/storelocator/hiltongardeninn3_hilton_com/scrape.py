import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hiltongardeninn3_hilton_com')


seesion = SgRequests()

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.hiltongardeninn3.hilton.com"
    
    region_id = ['34','402','21','25','23']
    for region in region_id:
        r = seesion.get("https://hiltongardeninn3.hilton.com/en_US/gi/ajax/cache/regionHotels.json?regionId="+str(region)).json()
        for data in r['hotels']:
            location_name = data['name']
            street_address = data['address1']
            city = data['city']
            state = data['state']
            zipp = data['zip'].replace("NL A1C0C1","A1C 0C1").replace("T2G-1N3","T2G 1N3")
            country_code = data['country'].replace("USA","US").replace("Canada","CA")
            store_number = "<MISSING>"
            if "phone" in data:
                phone = data['phone'].replace("+402","402")
            else:
                phone = "<MISSING>"
            location_type = "Hotel"
            latitude = data['lat']
            longitude = data['lng']
            hours = "<MISSING>"
            page_url = "https://www.hilton.com/en/hotels/"+str(data['ctyhocn'].lower())+"-"+str("-".join(data['url'].split("/")[-1].split("-")[:-1]))
            
            store =[]
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
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            # logger.info(store)
            yield store

    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


