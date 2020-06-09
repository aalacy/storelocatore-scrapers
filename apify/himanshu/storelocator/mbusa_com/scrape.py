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
    base_url = "https://www.mbusa.com"

    state_code = ['AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UM', 'UT', 'VT', 'VI', 'VA', 'WA', 'WV', 'WI', 'WY']
    for code in state_code:
        json_data = session.get("https://nafta-service.mbusa.com/api/dlrsrv/v1/us/search?count=10000&filter=mbdealer&state="+str(code)).json()['results']
        # loc_type = {"mbdealer":"Dealership","all":"All Locations","amg":"AMG Performance Center","amgelite":"AMG Performance Center Elite","collisioncenter":"Collision Center + Drop-off Locations","elitecollisioncenter":"Elite Collision Center (Aluminum Welding)","prmrexp":"Express Service by MB","service":"Service and Parts","maybach":"Maybach Dealership","zevst":"Zero Emission Vehicle State","sales":"Sales"}
        for data in json_data:
            location_name = data['name']
            street_address = (data['address'][0]['line1']+ str(data['address'][0]['line2'])).strip()
            city = data['address'][0]['city']
            state = data['address'][0]['state']
            zipp = data['address'][0]['zip']
            country_code = data['address'][0]['country']
            store_number = data['id']
            phone = data['contact'][0]['value']
            lat = data['address'][0]['location']['lat']
            lng = data['address'][0]['location']['lng']
            location_type = data['type']
            page_url = data['url']
            
            if data['activities'][-1]['url']:
                soup = bs(session.get(data['activities'][-1]['url']).text, "lxml")
                try:
                    if soup.find("div",{"class":re.compile("module-container js-module mod-department-hours mod-department-hours-theme2 mod-department-hours-theme2")}):
                        hr = soup.find("div",{"class":re.compile("module-container js-module mod-department-hours mod-department-hours-theme2 mod-department-hours-theme2")}).find("a",{"class":"js-popover"})['data-content']

                        hours = " ".join(list(bs(hr, "lxml").find("table").stripped_strings))
                    else:
                        try:
                            soup = bs(session.get(page_url+"/navigation-fragments/service-hours.htm?referrer=%2Fservice%2Fx-time.htm").text, "lxml")

                            hours = " ".join(list(soup.find("ul",{"class":"ddc-list-1 dictionary-list ddc-hours ddc-list-items list-unstyled"}).stripped_strings))
                        
                        except:
                            
                            hours = "<MISSING>"
                except:
                    hours = "<MISSING>"
            else:
                hours = "<MISSING>"
    
    
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
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)     
        
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            
            yield store
       
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
 
            
                
            
                
