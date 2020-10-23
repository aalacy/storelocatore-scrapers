import csv
import re
import json
import csv
from sgrequests import SgRequests
session = SgRequests()
from bs4 import BeautifulSoup
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('residence-inn_marriott_com')


base_url = 'https://residence-inn.marriott.com/'


def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://pacsys.marriott.com/data/marriott_properties_RI_en-US.json"
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    address=[]
    request = session.get(url, headers=headers)
    soup = BeautifulSoup(request.text,"lxml")
    data = (soup.text)
    store_list = json.loads(data)
    data_8 = (store_list['regions'])
    for i in data_8:
        for j in i['region_countries']:
            for k in j['country_states']:
                for h in k['state_cities']:
                    for g in (h['city_properties']):
                        if "USA" in (g['country_name']):
                            zipp = (g['postal_code'])
                            location_name = (g['name'])
                            street_address = (g['address'])
                            city = (g['city'])
                            state = (g['state_name'])
                            country_code = (g['country_name'])
                            phone = (g['phone'])
                            latitude = (g['latitude'])
                            longitude = (g['longitude'])
                            key = (g['marsha_code'])
                            page_url = "https://www.marriott.com/hotels/travel/"+str(key)
                            # logger.info(page_url)
                            output = []
                            output.append(base_url if base_url else "<MISSING>" ) # url
                            output.append(location_name if location_name else "<MISSING>") #location name
                            output.append(street_address if street_address else "<MISSING>") #address
                            output.append(city if city else "<MISSING>")#city
                            output.append(state if state else "<MISSING>") #state
                            output.append(zipp if zipp else "<MISSING>") #zipcode
                            output.append(country_code if country_code else "<MISSING>") #country code
                            output.append("<MISSING>") #store_number
                            output.append(phone if phone else "<MISSING>") #phone
                            output.append("Residence Inn by Marriott") #location type
                            output.append(latitude if latitude else "<MISSING>") #latitude
                            output.append(longitude if longitude else "<MISSING>") #longitude
                            output.append("<MISSING>") 
                            output.append(page_url if page_url else "<MISSING>")#opening hours  
                            if output[2] in address :
                                continue
                            address.append(output[2])    
                            for i in range(len(output)):
                                if type(output[i]) == str:
                                    output[i] = ''.join((c for c in unicodedata.normalize('NFD', output[i]) if unicodedata.category(c) != 'Mn'))
                            output = [x.replace("–","-") if type(x) == str else x for x in output]
                            output = [x.encode('ascii', 'ignore').decode('ascii') if type(x) == str else x for x in output]      
                            yield output
    for i1 in data_8:
        # logger.info(i1)
        for j1 in i1['region_countries']:
            for k1 in j1['country_states']:
                # logger.info(k1)
                for h1 in k1['state_cities']:
                    for g1 in (h1['city_properties']):
                        if "CA" in (g1['country_code']):
                            zipp = (g1['postal_code'])
                            location_name = (g1['name'])
                            street_address = (g1['address'])
                            city = (g1['city'])
                            state = (g1['state_name'])
                            country_code = (g1['country_name'])
                            phone = (g1['phone'])
                            latitude = (g1['latitude'])
                            longitude = (g1['longitude'])
                            key = (g1['marsha_code'])
                            page_url = "https://www.marriott.com/hotels/travel/"+str(key)
                            # logger.info(page_url)
                            output = []
                            output.append(base_url if base_url else "<MISSING>" ) # url
                            output.append(location_name if location_name else "<MISSING>") #location name
                            output.append(street_address if street_address else "<MISSING>") #address
                            output.append(city if city else "<MISSING>")#city
                            output.append(state if state else "<MISSING>") #state
                            output.append(zipp if zipp else "<MISSING>") #zipcode
                            output.append(country_code if country_code else "<MISSING>") #country code
                            output.append("<MISSING>") #store_number
                            output.append(phone if phone else "<MISSING>") #phone
                            output.append("Residence Inn by Marriott") #location type
                            output.append(latitude if latitude else "<MISSING>") #latitude
                            output.append(longitude if longitude else "<MISSING>") #longitude
                            output.append("<MISSING>") 
                            output.append(page_url if page_url else "<MISSING>")#opening hours 
                            if output[2] in address :
                                continue
                            address.append(output[2])    
                            for i in range(len(output)):
                                if type(output[i]) == str:
                                    output[i] = ''.join((c for c in unicodedata.normalize('NFD', output[i]) if unicodedata.category(c) != 'Mn'))
                            output = [x.replace("–","-") if type(x) == str else x for x in output]
                            output = [x.encode('ascii', 'ignore').decode('ascii') if type(x) == str else x for x in output]  
                            yield output
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
