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
    dummy =[]
    MAX_RESULTS = 50
    MAX_DISTANCE = 40
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US',"CA"])
    
    urls ="https://dealerlocator.deere.com/servlet/country=US?locale=en_US#"
    responses= bs(requests.get( urls).text,'lxml')
    # tag_phone = responses.find(lambda tag: (tag.name == "script" or tag.name == "h2") and "var industries" in tag.text.strip())
    # array1 = (responses.text.split("var industries =")[1].split("var productGroups")[0].replace("];","]"))
    coord = search.next_coord()
    current_results_len = 0
    response={}
    base_url = "https://www.deere.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
   # print("url")
    while coord:
        result_coords =[]
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        KP=[
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
        for i in KP:
            url ="https://dealerlocator.deere.com/servlet/ajax/getLocations?lat="+str(coord[0])+"&long="+str(coord[1])+"&locale=en_US&country=US&uom=MI&filterElement="+str(i['id'])
          #  print(url)
            try:
                response = requests.get( url, headers=headers).json()
            except:
                pass
            if "locations" in response:
                for data in response['locations']:
                    zipp1=''
                    page_url=''
                    latitude = data['latitude']
                    longitude = data['longitude']
                    location_name = data['locationName']
                    page_url = data['seoFriendlyUrl']
                    # print(page_url)
                    response2 = bs(requests.get(page_url, headers=headers).text,'lxml')
                    try:
                        try:
                            street_address = list(response2.find("p",{"class":"address"}).stripped_strings)[0].split(",")[0]
                            city = list(response2.find("p",{"class":"address"}).stripped_strings)[0].split(",")[1].strip()
                            state = list(response2.find("p",{"class":"address"}).stripped_strings)[0].split(",")[2].strip().split()[0]
                            zipp = (" ".join(list(response2.find("p",{"class":"address"}).stripped_strings)[0].split(",")[2].strip().split()[1:]))
                        except:
                            street_address = list(response2.find("div",{"class":"destination"}).find_all("p")[-1].stripped_strings)[0].split(",")[0]
                            city = list(response2.find("div",{"class":"destination"}).find_all("p")[-1].stripped_strings)[0].split(",")[1].strip()
                            state = list(response2.find("div",{"class":"destination"}).find_all("p")[-1].stripped_strings)[0].split(",")[2].strip().split()[0]
                            zipp = (" ".join(list(response2.find("div",{"class":"destination"}).find_all("p")[-1].stripped_strings)[0].split(",")[2].strip().split()[1:]))
                    except:
                        pass
                    # street_address = " ".join(data['formattedAddress'][:-1])
                    # zipp1 = data['formattedAddress'][-1].split( )[-1]
                    # state = data['formattedAddress'][-1].split( )[-2]
                    # city = " ".join(data['formattedAddress'][-1].split( )[:-2])
                    phone = data['contactDetail']['phone']
                    store_number = "<MISSING>"
                    hours = "<MISSING>"
                    store = [] 
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)   
                    store.append("US")
                    store.append(store_number)
                    store.append(phone)
                    store.append(i['name'])
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours if hours else "<MISSING>")
                    store.append(page_url if page_url else "<MISSING>")
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    if store[2] in dummy:
                        continue
                    dummy.append(store[2])
                  #  print(store)  
                    yield store
            responses=''
            url ="https://dealerlocator.deere.com/servlet/ajax/getLocations?lat="+str(coord[0])+"&long="+str(coord[1])+"&locale=en_GB&country=CA&uom=KM&filterElement="+str(i['id'])
            try:
                responses = requests.get(url , headers=headers).json()
            except:
                pass
            if "locations" in responses:
                for data in responses['locations']:
                    zipp=''
                    page_url=''
                    latitude = data['latitude']
                    longitude = data['longitude']
                    location_name = data['locationName']
                    page_url = data['seoFriendlyUrl']
                    print(page_url)
                    response1 = bs(requests.get(page_url, headers=headers).text,'lxml')
                    try:
                        try:
                            add = list(response1.find("p",{"class":"address"}).stripped_strings)[0].split(",")
                        except:
                            add = list(response1.find("div",{"class":"destination"}).find_all("p")[-1].stripped_strings)[0].split(",")
                    except:
                        pass
                    # print(add)
                    try:
                        street_address = " ".join(add[:-2])
                        city = add[-2].strip()
                        state = add[-1].strip().split()[0]
                        zipp = (" ".join(add[-1].strip().split()[1:]))
                    except:
                        pass
          
                    phone = data['contactDetail']['phone']
                    store_number = "<MISSING>"
                    hours=""
                    hours = "<MISSING>"
                    store = []
                    # state_list = re.findall(r' ([A-Z]{2})', str(data['formattedAddress'][-1]))
                    # if state_list:
                    #     state = state_list[-1]
                    # city = data['formattedAddress'][-1].split(state)[0]
                    # zipp = data['formattedAddress'][-1].split(state)[-1]
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
                    # print(store)  
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


