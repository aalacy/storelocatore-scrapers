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
    # array2=responses.text.split("var productGroups =")[1].split('var locale = "en_US";')[0].replace("];",']').replace("\'s",'Lowe')
    # print(array2)
    # print(json.loads(array2))
    # exit()
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
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        KP=[{ "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 68, "name": "Scraper Tractors" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 60, "name": "Compact Construction Equipment" }, { "id": 61, "name": "Compact Excavators" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 41, "name": "ProGator\u2122 and TX Turf Gator Utility Vehicles" }, { "id": 47, "name": "Skid Steers" }, { "id": 70, "name": "Self-Propelled Forage Harvesters" }, { "id": 61, "name": "Compact Excavators" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 27, "name": "Funk Drivetrain Components - Sales" }, { "id": 23, "name": "Flail Mowers" }, { "id": 24, "name": "Flail Shredders" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 20, "name": "Engines (On-Highway), Natural Gas-Service" }, { "id": 36, "name": "Knuckleboom Loaders" }, { "id": 33, "name": "Harvesting (Grain, Cotton, Sugar)" }, { "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 58, "name": "Construction Attachments" }, { "id": 64, "name": "Tractor Loaders (Construction)" }, { "id": 47, "name": "Skid Steers" }, { "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 22, "name": "Excavators" }, { "id": 28, "name": "Funk Drivetrain Components - Service" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 47, "name": "Skid Steers" }, { "id": 62, "name": "Compact Track Loaders" }, { "id": 47, "name": "Skid Steers" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 62, "name": "Compact Track Loaders" }, { "id": 26, "name": "Forwarders" }, { "id": 61, "name": "Compact Excavators" }, { "id": 57, "name": "Wheel Loaders" }, { "id": 55, "name": "Walk-Behind Mowers" }, { "id": 44, "name": "Scotts Mowers (Service Only)" }, { "id": 32, "name": "Harvesters" }, { "id": 51, "name": "Tillage" }, { "id": 12, "name": "Commercial Mowing Equipment" }, { "id": 65, "name": "Feller Bunchers" }, { "id": 43, "name": "Riding Mowers & Zero-Turn Mowers" }, { "id": 59, "name": "Tractors - Compact (20-66 engine hp)" }, { "id": 25, "name": "Swing Machines" }, { "id": 69, "name": "Scraper Tractors (Construction)" }, { "id": 66, "name": "Tractor Loaders" }, { "id": 16, "name": "Crawler Loaders" }, { "id": 50, "name": "Snow Equipment" }, { "id": 38, "name": "Motor Graders" }, { "id": 60, "name": "Compact Construction Equipment" }, { "id": 30, "name": "Golf & Sports Mowing Equipment" }, { "id": 34, "name": "Hay & Forage" }, { "id": 40, "name": "Planting & Seeding" }, { "id": 35, "name": "John Deere sold at Lowes and The Home Depot (Service Only)" }, { "id": 47, "name": "Skid Steers" }, { "id": 10, "name": "Backhoe Loaders" }, { "id": 19, "name": "Engines (Off-Highway), Industrial - Service" }, { "id": 21, "name": "Engines, Marine- Sales & Service" }, { "id": 11, "name": "Bunker\/Field Rakes" }, { "id": 42, "name": "Rotary Cutters" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 18, "name": "Engines (Off-Highway), Industrial - Sales" }, { "id": 49, "name": "Skidders" }, { "id": 8, "name": "Articulated Dump Trucks" }, { "id": 94, "name": "Crawler Dozers (under 105 hp)" }, { "id": 46, "name": "Self-Propelled Sprayers & Nutrient Applicators" }, { "id": 59, "name": "Tractors - Compact (20-66 engine hp)" }, { "id": 58, "name": "Construction Attachments" }, { "id": 96, "name": "Crawler Dozers (over 105 hp)" }, { "id": 17, "name": "Crawler Dozers (Forestry)" }, { "id": 54, "name": "Tractors - Large (210-620 engine hp)" }, { "id": 45, "name": "Scrapers" }, { "id": 57, "name": "Wheel Loaders" }, { "id": 59, "name": "Tractors - Compact (20-66 engine hp)" }, { "id": 7, "name": "Agriculture" }, { "id": 6, "name": "Lawn & Garden" }, { "id": 97, "name": "Landscaping & Grounds Care" }, { "id": 2, "name": "Construction" }, { "id": 3, "name": "Engines & Drivetrain" }, { "id": 5, "name": "Golf & Sports" }, { "id": 4, "name": "Forestry" }, { "id": 60, "name": "Compact Construction Equipment" }, { "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 68, "name": "Scraper Tractors" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 60, "name": "Compact Construction Equipment" }, { "id": 61, "name": "Compact Excavators" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 41, "name": "ProGator\u2122 and TX Turf Gator Utility Vehicles" }, { "id": 47, "name": "Skid Steers" }, { "id": 70, "name": "Self-Propelled Forage Harvesters" }, { "id": 61, "name": "Compact Excavators" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 27, "name": "Funk Drivetrain Components - Sales" }, { "id": 23, "name": "Flail Mowers" }, { "id": 24, "name": "Flail Shredders" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 20, "name": "Engines (On-Highway), Natural Gas-Service" }, { "id": 36, "name": "Knuckleboom Loaders" }, { "id": 33, "name": "Harvesting (Grain, Cotton, Sugar)" }, { "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 58, "name": "Construction Attachments" }, { "id": 64, "name": "Tractor Loaders (Construction)" }, { "id": 47, "name": "Skid Steers" }, { "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 22, "name": "Excavators" }, { "id": 28, "name": "Funk Drivetrain Components - Service" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 47, "name": "Skid Steers" }, { "id": 62, "name": "Compact Track Loaders" }, { "id": 47, "name": "Skid Steers" }, { "id": 52, "name": "Tractors - Mid (105-215 engine hp)" }, { "id": 62, "name": "Compact Track Loaders" }, { "id": 26, "name": "Forwarders" }, { "id": 61, "name": "Compact Excavators" }, { "id": 57, "name": "Wheel Loaders" }, { "id": 55, "name": "Walk-Behind Mowers" }, { "id": 44, "name": "Scotts Mowers (Service Only)" }, { "id": 32, "name": "Harvesters" }, { "id": 51, "name": "Tillage" }, { "id": 12, "name": "Commercial Mowing Equipment" }, { "id": 65, "name": "Feller Bunchers" }, { "id": 43, "name": "Riding Mowers & Zero-Turn Mowers" }, { "id": 59, "name": "Tractors - Compact (20-66 engine hp)" }, { "id": 25, "name": "Swing Machines" }, { "id": 69, "name": "Scraper Tractors (Construction)" }, { "id": 66, "name": "Tractor Loaders" }, { "id": 16, "name": "Crawler Loaders" }, { "id": 50, "name": "Snow Equipment" }, { "id": 38, "name": "Motor Graders" }, { "id": 60, "name": "Compact Construction Equipment" }, { "id": 30, "name": "Golf & Sports Mowing Equipment" }, { "id": 34, "name": "Hay & Forage" }, { "id": 40, "name": "Planting & Seeding" }, { "id": 35, "name": "John Deere sold at Lowes and The Home Depot (Service Only)" }, { "id": 47, "name": "Skid Steers" }, { "id": 10, "name": "Backhoe Loaders" }, { "id": 19, "name": "Engines (Off-Highway), Industrial - Service" }, { "id": 21, "name": "Engines, Marine- Sales & Service" }, { "id": 11, "name": "Bunker\/Field Rakes" }, { "id": 42, "name": "Rotary Cutters" }, { "id": 29, "name": "Gator\u2122 Utility Vehicles" }, { "id": 53, "name": "Tractors - Small (45-125 engine hp)" }, { "id": 18, "name": "Engines (Off-Highway), Industrial - Sales" }, { "id": 49, "name": "Skidders" }, { "id": 8, "name": "Articulated Dump Trucks" }, { "id": 94, "name": "Crawler Dozers (under 105 hp)" }, { "id": 46, "name": "Self-Propelled Sprayers & Nutrient Applicators" }, { "id": 59, "name": "Tractors - Compact (20-66 engine hp)" }, { "id": 58, "name": "Construction Attachments" }, { "id": 96, "name": "Crawler Dozers (over 105 hp)" }, { "id": 17, "name": "Crawler Dozers (Forestry)" }, { "id": 54, "name": "Tractors - Large (210-620 engine hp)" }, { "id": 45, "name": "Scrapers" }, { "id": 57, "name": "Wheel Loaders" }, { "id": 59, "name": "Tractors - Compact (20-66 engine hp)" } ]
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
                    if len(zipp1) != 5:
                        index = 5
                        char = '-'
                        zipp1 = zipp1[:index] + char + zipp1[index + 1:]
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
                    # print(store)
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


