import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    base_url = "https://www.mercedes-benz.co.uk/"

    headers = {
        'x-apikey': '45ab9277-3014-4c9e-b059-6c0542ad9484'
    }
    externalId = session.get("https://api.corpinter.net/dlc/dms/v2/dealers/search?strictGeo=true&marketCode=GB&configurationExternalId=Dlp&searchProfileName=DLp_gb&distance=25mi", headers=headers).json()['results']
    for eId in externalId:
        
        json_data = session.get("https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields=*&whiteList="+eId['baseInfo']['externalId'], headers=headers).json()['results']
    
        for data in json_data:
            location_name = data['baseInfo']['name1']
            street_address = data['address']['line1']
            city = data['address']['city']
            try:
                state = data['address']['region']['region']
            except:
                state = "<MISSING>"
            zipp = data['address']['zipcode']
            country_code = data['address']['country']
            store_number = data['baseInfo']['externalId'].replace("GS","")
            try:
                phone = data['contact']['phone']
            except:
                phone = "<MISSING>"
            lat = data['address']['latitude']
            lng = data['address']['longitude']
            try:
                page_url = data['contact']['website']
            except:
                page_url = "<MISSING>"
            counter = 0
            hours = ''
            for hr in data['functions']:
                if counter == 1:
                    break
                if 'openingHours' in hr:
                    for key,value in hr['openingHours'].items():
                        if value['open'] == True:
                            hours+= key +": "+ value['timePeriods'][0]['from']+" - "+ value['timePeriods'][0]['to'] + " " 
                        else:
                            key +": Closed"
                else:
                    hours = "<MISSING>"

                
                counter+= 1
           
            
    


            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address.replace('None',''))
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours.strip())
            store.append(page_url)     
        
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            
            yield store
        
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
 
            
                
            
                
