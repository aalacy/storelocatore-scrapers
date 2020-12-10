import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cardsmart_com')



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
    addressess=[]
    base_url = "https://www.cardsmart.com"
    r = session.get("https://app.locatedmap.com/initwidget/?instanceId=338377d9-797b-4382-8235-f418c4032fea&compId=comp-j6cb5nsq&viewMode=text&styleId=style-k34xbuey").json()
    for i in json.loads(r['mapSettings'].replace("\n",'')):
        for data in i['fields']['unpublishedLocations']:
            latitude= data['latitude']
            longitude = data['longitude']
            opening_hours = data['opening_hours']
            phone =data['tel']
            location_name = data['name']
            page_url = data['website']
            address = usaddress.parse(data['formatted_address'])
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address))
            if us_zip_list:
                zipp = us_zip_list[-1]
            city = []
            state = []
            street_address = []
            for info in address:
                if 'PlaceName' in info:
                    city.append(info[0])
                if "StateName" in info:
                    state.append(info[0])
                if "AddressNumber" in info:
                    street_address.append(info[0])
                if "StreetNamePreType" in info:
                    street_address.append(info[0])
                if "StreetName" in info:
                    street_address.append(info[0])
                if "StreetNamePostType" in info:
                    street_address.append(info[0])
                if "StreetNamePostDirectional" in info:
                    street_address.append(info[0])
                if "OccupancyType" in info:
                    street_address.append(info[0])
                if "OccupancyIdentifier" in info:
                    street_address.append(info[0])
            street_address = " ".join(street_address).replace(",","").replace("Ave.","Avenue")
            city = " ".join(city).replace(",","")
            state = " ".join(state).replace(",","").replace("PEI","PE").replace("Wisconsin","WI").replace("BC BC","BC").replace("Champlin","").replace("La QC","QC")
            if "101 21st St" in street_address:
                city = 'Nitro'
                state = 'West Virginia'

            if "3109 US Highway 9 Old Bridge" in street_address:
                city = 'Old Bridge'
                state = 'New Jersey'
                street_address=street_address.replace("3109 US Highway 9 Old Bridge",'3109 US Highway 9')
            
            if "445 Putnam Pike" in street_address:
                state = 'Rhode Island'

            if "5th St W" in street_address or "1419 US-60 E" in street_address:
                city = 'Huntington'
                state = 'West Virginia'
            if "211 Bowman St" in street_address:
                city = 'Spencer'
                state = 'West Virginia'

            if "209 Church St" in street_address:
                city = 'Ripley'
                state = 'West Virginia'
                street_address=street_address.replace("209 Church St",'209 S Church St')
            if "1506 Elizabeth Pike" in street_address or "125 7th Ave" in street_address or "501 Roosevelt Blvd" in street_address or "425 Camden Rd" in street_address or "4016 Ohio River Rd" in street_address or "4539 Teays Valley Rd" in street_address :
                state = 'West Virginia'
            
            if "2501 Jackson Ave" in street_address:
                city = 'Point Pleasant'
                state = 'West Virginia'
            
            if "101 21st St" in street_address:
                city = 'Nitro'
                state = 'West Virginia'

            if "601 Broadway" in street_address or "370C Market St" in street_address or "578 Valley Rd" in street_address or "40 Chatham Rd" in street_address:
                state = 'New Jersey'
            # logger.info(city)
            store=[]
            store.append("https://www.cardsmart.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city.replace("West Virginia",'').replace("New Jersey",'').replace("Rhode Island",''))
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(opening_hours.replace("\n",' ').replace("Store Hours:",'').strip() if opening_hours else "<MISSING>")
            if "facebook" in page_url:
                page_url="<MISSING>"
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
          
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            # logger.info("----------------------",store)
            yield store
   
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
