
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
import sgzip
session = SgRequests()
import requests
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
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['gb'])
    MAX_RESULTS = 100
    MAX_DISTANCE = 25
    coord = search.next_coord()
    base_url = "https://www.fiat.co.uk/"

    while coord:
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        result_coords = []
        soup = bs(session.get("https://dealerlocator.fiat.com/geocall/RestServlet?jsonp=callback&mkt=3112&brand=00&func=finddealerxml&serv=sales&track=1&x="+str(coord[1])+"&y="+str(coord[0])+"&rad=100&_=1591185101147").content, "lxml")
        try:
            json_data = json.loads(soup.find("p").text.split("callback(")[1].replace("]})","]}"))['results']
            
            for data in json_data:
                
                location_name = data['COMPANYNAM']
                street_address = re.sub(r'\s+'," ",data['ADDRESS']).strip()
                city = data['TOWN']
                state = data['PROVINCE']
                zipp = data['ZIPCODE'].replace("_"," ")
                phone = data['TEL_1']
                lat = data['YCOORD']
                lng = data['XCOORD']
                page_url = data['WEBSITE']
                
                if page_url == " ":
                    page_url = "<MISSING>"
                store_number = data['MAINCODE']
                
                hours = ''
                hr_value = data['ACTIVITY'][0]
                for key,value in hr_value.items():
                    if "DATEWEEK" in hr_value[key]:
                        if "MORNING_FROM" in hr_value[key]:
                            if "AFTERNOON_TO" in hr_value[key] and "MORNING_FROM" in hr_value[key]:
                                hours+= " "+ hr_value[key]['DATEWEEK']+" "+datetime.strptime(hr_value[key]['MORNING_FROM'],"%H%M").strftime("%I:%M %p")+"-"+datetime.strptime(hr_value[key]['AFTERNOON_TO'],"%H%M").strftime("%I:%M %p")
                            else:
                                hours+=  " "+hr_value[key]['DATEWEEK']+ " Closed"
                        else:
                            hours+=  " "+hr_value[key]['DATEWEEK']+ " Closed"

            
                
                result_coords.append((lat,lng))
                store = []
                store.append(base_url if base_url else "<MISSING>")
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")   
                store.append("UK")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hours if hours else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")     
            
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
        except:
            pass
        if len(json_data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
