import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
import phonenumbers
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('foodsco_net')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    states = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH",'OK',"OR","PA","RI","SC","SD",'TN',"TX","UT","VT","VA","WA","WV","WI","WY"]
    addresses = []
    locator_domain = 'https://www.foodsco.net/'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    for state in states:
        logger.info(state)
        r = session.get("https://www.foodsco.net/stores/search?searchText="+str(state), headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        str1 = '{"stores":'+soup.find(lambda tag: (tag.name == "script") and "window.__INITIAL_STATE__ =" in tag.text).text.split('"stores":')[1].split(',"shouldShowFuelMessage":true}')[0]+"}"
        json_data = json.loads(str1.replace("\\",""))
        # logger.info(json_data)
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
    ##### store
    
        datas = json_data['stores']
        for key in datas:
            if key["banner"]:
                if "FOODSCO" not in key["banner"]:
                    continue
                    # logger.info("ltype == ",key["banner"])
                location_type = "foodsco"
                # logger.info(location_type)
                location_name = key['vanityName']
                street_address = key['address']['addressLine1'].capitalize()
                city = key['address']['city'].capitalize()
                state = key['address']['stateCode']
                zipp =  key['address']['zip']
                country_code = key['address']['countryCode']
                store_number = key['storeNumber']
                if key['phoneNumber']:
                    phone = phonenumbers.format_number(phonenumbers.parse(str(key['phoneNumber']), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
                else:
                    phone = "<MISSING>"
                latitude = key['latitude']
                longitude = key['longitude']  
                page_url = "https://www.foodsco.net/stores/details/"+str(key['divisionNumber'])+"/"+str(store_number)
                hours_of_operation = ""
                for day_hours in key["ungroupedFormattedHours"]:
                    hours_of_operation += day_hours["displayName"] +  " = " + day_hours["displayHours"] + "  "
                

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if (store[-7]) in addresses:
                    continue
                addresses.append(store[-7])
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',)
                yield store

    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
