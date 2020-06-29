import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import requests
session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    adressess = []
    adressess1 =[]
    MAX_RESULTS = 50
    MAX_DISTANCE = 40
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US',"CA"])
    
    urls ="https://dealerlocator.deere.com/servlet/country=US?locale=en_US#"
    responses= bs(requests.get( urls).text,'lxml')
    tag_phone = responses.find(lambda tag: (tag.name == "script" or tag.name == "h2") and "var industries" in tag.text.strip())
    array1 = (responses.text.split("var industries =")[1].split("var productGroups")[0].replace("];","]"))
    coord = search.next_coord()
    current_results_len = 0
    response={}
    base_url = "https://www.deere.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    while coord:
        result_coords =[]

        KP = [{ "id": 7, "name": "Agriculture" }, { "id": 6, "name": "Lawn & Garden" }, { "id": 97, "name": "Landscaping & Grounds Care" }, { "id": 2, "name": "Construction" }, { "id": 3, "name": "Engines & Drivetrain" }, { "id": 5, "name": "Golf & Sports" }, { "id": 4, "name": "Forestry" }, { "id": 60, "name": "Compact Construction Equipment" }]
        for i in KP:
            url ="https://dealerlocator.deere.com/servlet/ajax/getLocations?lat="+str(coord[0])+"&long="+str(coord[1])+"&locale=en_US&country=US&uom=MI&filterElement="+str(i['id'])
            try:
                response = requests.get( url, headers=headers).json()
            except:
                pass
            if "locations" in response:
                for data in response['locations']:
                    latitude = data['latitude']
                    longitude = data['longitude']
                    location_name = data['locationName']
                    page_url = data['seoFriendlyUrl']
                    street_address = " ".join(data['formattedAddress'][:-1])
                    zipp1 = data['formattedAddress'][-1].split( )[-1]
                    state = data['formattedAddress'][-1].split( )[-2]
                    city = " ".join(data['formattedAddress'][-1].split( )[:-2])
                    phone = data['contactDetail']['phone']
                    store_number = "<MISSING>"
                    hours=""
                    hours = "<MISSING>"
                    try:
                        if len(zipp1) != 5 and type(int(zipp1))==int:
                            index = 5
                            char = '-'
                            zipp1 = zipp1[:index] + char + zipp1[index + 1:]
                    except:
                        zipp1 =zipp1
                    store = [] 
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp1)   
                    store.append("US")
                    store.append(store_number)
                    store.append(phone)
                    store.append(i['name'])
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours if hours else "<MISSING>")
                    store.append(page_url if page_url else "<MISSING>")     
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    if store[2] in adressess:
                        continue
                    adressess.append(store[2])
                    yield store

            url ="https://dealerlocator.deere.com/servlet/ajax/getLocations?lat="+str(coord[0])+"&long="+str(coord[1])+"&locale=en_GB&country=CA&uom=KM&filterElement="+str(i['id'])
            try:
                response = requests.get( url, headers=headers).json()
            except:
                pass
            if "locations" in response:
                for data in response['locations']:
                    latitude = data['latitude']
                    longitude = data['longitude']
                    location_name = data['locationName']
                    page_url = data['seoFriendlyUrl']
                    street_address = " ".join(data['formattedAddress'][:-1])
                    zipp = data['formattedAddress'][-1].split( )[-1]
                    city = " ".join(data['formattedAddress'][-1].split( )[:-2])
                    phone = data['contactDetail']['phone']
                    store_number = "<MISSING>"
                    hours=""
                    hours = "<MISSING>"
                    store = []
                    state_list = re.findall(r' ([A-Z]{2})', str(data['formattedAddress'][-1]))
                    if state_list:
                        state = state_list[-1]
                    city = data['formattedAddress'][-1].split(state)[0]
                    zipp = data['formattedAddress'][-1].split(state)[-1]
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)   
                    store.append("CA")
                    store.append(store_number)
                    store.append(phone)
                    store.append(i['name'])
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours if hours else "<MISSING>")
                    store.append(page_url if page_url else "<MISSING>")     
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    if store[2] in adressess1:
                        continue
                    adressess1.append(store[2])
                    # print(store)
                    yield store
             
        if current_results_len < MAX_RESULTS:
                # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()


