import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    states_coord = {"location":[{"state":"FL","centerLat":"27.6648274","centerLng":"-81.5157535"},{"state":"GA","centerLat":"32.1656221","centerLng":"-82.9000751"},{"state":"NC","centerLat":"35.7595731","centerLng":"-79.01929969999999"},{"state":"SC","centerLat":"33.836081","centerLng":"-81.1637245"}]}

    for cord in states_coord['location']:
        
    
        payload = "{\"location\":\""+str(cord['state'])+"\",\"city\":\"\",\"state\":\""+str(cord['state'])+"\",\"zip\":\"\",\"checkedValues\":\"\",\"centerLat\":\""+str(cord['centerLat'])+"\",\"centerLng\":\""+str(cord['centerLng'])+"\"}"

        
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            }

        json_data = session.post("http://www.pruitthealth.com/_Layouts/FacilityLocatorSt/FacilityLocatorSt.aspx/FilterFacilityByFeatures", data=payload, headers=headers).json()['d']['mapData']
        for data in json.loads(json_data):
            location_name = data['Title']
            
            if len(data['Address'].split(",")) == 3:
                street_address = " ".join(data['Address'].split(",")[:-2])
                city = data['Address'].split(",")[-2].strip()
                state = data['Address'].split(",")[-1].replace("South Carolina","SC").split()[0]
                zipp = data['Address'].split(",")[-1].replace("South Carolina","SC").split()[1]

            elif len(data['Address'].split(",")) == 4:

                if len(data['Address'].split(",")[-1].split()) == 1:
                    street_address = data['Address'].split(",")[0]
                    city = data['Address'].split(",")[1].strip()
                    state = data['Address'].split(",")[-2].strip()
                    zipp = data['Address'].split(",")[-1].strip()
                else:
                    street_address = " ".join(data['Address'].split(",")[:-2])
                    city = data['Address'].split(",")[-2].strip()
                    state = data['Address'].split(",")[-1].split()[0]
                    zipp = data['Address'].split(",")[-1].split()[1]
            elif len(data['Address'].split(",")) == 2:

                addr = data['Address'].split(",")
                if "USA" in addr[-1]:
                    del addr[-1]
                if len(addr) == 1:
                    street_address = "<MISSING>"
                    city = " ".join(addr[0].split()[:-2])
                    state = addr[0].split()[-2]
                    zipp = addr[0].split()[-1]
                else:
                    try:
                        if len(addr[-1].split()) == 3:
                            street_address = addr[0]
                            city = addr[-1].split()[0]
                            state = addr[-1].split()[1]
                            zipp = addr[-1].split()[2]
                        else:
                            street_address = " ".join(addr[0].split()[:-1])
                            city = addr[0].split()[-1]
                            state = addr[-1].split()[-2]
                            zipp = addr[-1].split()[-1]
                    except:
                        street_address = addr[0]
                        city = "<MISSING>"
                        state = "<MISSING>"
                        zipp = addr[-1].strip()
                
            else:
                street_address = " ".join(data['Address'].split(",")[:-3])
                city = data['Address'].split(",")[-3].strip()
                state = data['Address'].split(",")[-2].strip()
                zipp = data['Address'].split(",")[-1].strip()
           
            

            latitude = data['Latitude']
            longitude = data['Longitude']
            store_number = data['Id']
            soup = BeautifulSoup(data['Body'], "lxml")
            phone = soup.find("span",{"class":"phn-no"}).text
            page_url = "http://www.pruitthealth.com/microsite?facilityId="+str(store_number)

            store = []
            store.append("http://www.pruitthealth.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url)
           
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            
            yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
