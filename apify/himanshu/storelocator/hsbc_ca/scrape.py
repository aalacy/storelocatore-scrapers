import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hsbc_ca')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.hsbc.ca"
  
    return_main_object = []
    addresses = []
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 51
    MAX_DISTANCE = 20
    current_results_len = 0
    coord = search.next_zip()
    
    while coord:
        result_coords = []

        lat = str(coord[0])
        lng = str(coord[1])
        phone =''
        # r1 = session.get(base_url + zp['href'])
        # soup1 = BeautifulSoup(r.text, 'lxml')
        try:
            r2 = session.get('https://www.hsbc.ca/1/PA_ABSL-JSR168/ABSLFCServlet?event=cmd_ajax&location_type=show-all-results&address=&cLat='+lat+'&cLng='+lng+'&LOCALE=en&rand='+str(MAX_DISTANCE)).json()
        except:
            continue
        current_results_len = len(r2['results'])
        for dt in r2['results']:
            # storeno=dt['location']['locationId']
            storeno = "<MISSING>"
            name = dt['location']['name']
            address=dt['location']['address']['postalAddress']
            address = dt['location']['address']['postalAddress']
            state = dt['location']['address']['province']
            city = dt['location']['address']['city']
            zip = dt['location']['address']['postalCode']
            country = dt['location']['address']['country']
            location_type = dt['location']['links']['details_tab']
            if dt['location']['contacts'] != None:
                # phone = dt['location']['contacts'][-1].split("Phone|")[-1] 
                phone= re.sub(r'[a-zA-Z|]', '', dt['location']['contacts'][-1])
                #logger.info(phone)
            if country == "Canada":
                country="CA"
            # logger.info("==========================================")
            lat=dt['location']['address']['lat']
            lng=dt['location']['address']['lng']
            store=[]
            hour=''
            if "services" in dt['location']:
                if dt['location']['services']:
                    hour=dt['location']['services'][0]
            if "WorkHrs" in dt['location']:
                for i in dt['location']['WorkHrs']['lobby']:
                   if  dt['location']['WorkHrs']['lobby'][i]=="-":
                        hour+=' '+i+' '+"Closed"
                   else:
                       hour+=' '+i+' '+dt['location']['WorkHrs']['lobby'][i]

            result_coords.append((lat, lng))
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<MISSING>")
            store.append( "<MISSING>")
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            # logger.info(store)
            yield store

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
