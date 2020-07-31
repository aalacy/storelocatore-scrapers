import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
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

    dummy =[]
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US', 'CA'])

    coord = search.next_coord()
    base_url = "https://www.deere.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
    }

    while coord:
        result_coords =[]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        filterElement=[
				{
					"id":7,
         			"name":"Agriculture"
				},
				
				{
					"id":6,
         			"name":"Lawn & Garden"
				},
				
				{
					"id":97,
         			"name":"Landscaping & Grounds Care"
				},
				
				{
					"id":2,
         			"name":"Construction"
				},
				
				{
					"id":3,
         			"name":"Engines & Drivetrain"
				},
				
				{
					"id":5,
         			"name":"Golf & Sports"
				},
				
				{
					"id":4,
         			"name":"Forestry"
				},
				
				{
					"id":60,
         			"name":"Compact Construction Equipment"
				} ]
        current_results_len = 0
        for f_ele in filterElement:

            url ="https://dealerlocator.deere.com/servlet/ajax/getLocations?lat="+str(coord[0])+"&long="+str(coord[1])+"&locale=en_US&country=CA&uom=KM&filterElement="+str(f_ele['id'])
            
            try:
                responses = session.get(url , headers=headers).json()
            except:
                continue
            
    
            if "locations" in responses:
                current_results_len += len(responses['locations'])
    
                for data in responses['locations']:
                
                    latitude = data['latitude']
                    longitude = data['longitude']
                    location_name = data['locationName']
                    page_url = data['seoFriendlyUrl']
                    phone = data['contactDetail']['phone']
                    store_number = data['locationId']
                    street_address = " ".join(data['formattedAddress'][:-1])
                    
                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(data['formattedAddress'][-1]))
                   
                    state_list = re.findall(r' ([A-Z]{2}) ', str(data['formattedAddress'][-1]))
                    state = state_list[-1]
                    zipp = ca_zip_list[-1]
                    city = data['formattedAddress'][-1].replace(state,"").replace(zipp,"").replace(",","").strip()
                    
                    result_coords.append((latitude,longitude))
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)   
                    store.append("CA")
                    store.append(store_number)
                    store.append(phone)
                    store.append(f_ele['name'])
                    store.append(latitude)
                    store.append(longitude)
                    store.append("<MISSING>")
                    store.append(page_url)
                    
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    if store[2] in dummy:
                        continue
                    dummy.append(store[2])

                    yield store
            else:
                continue
        

        search.max_count_update(result_coords)
        coord = search.next_coord()
               

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


