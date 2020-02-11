import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from tenacity import *
import timeout_decorator

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

@timeout_decorator.timeout(30)
def query_locator(zip_code):
    return session.get("https://locations.comerica.com/?q={}&filter=bc".format(zip_code))
 

def fetch_data():
    return_main_object = []
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    base_url = "https://www.comerica.com"

    while zip_code:
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        result_coords = []
        location_name =''
        try:
            r = query_locator(zip_code)
        except:
            zip_code = search.next_zip()
            continue
        soup=BeautifulSoup(r.text ,"lxml")
        return_main_object = []
        main=soup.find_all('script')
        for script in main:
            if re.search("var results" ,script.text):
                loc=json.loads(script.text.split('var results = ')[1].split('var map;')[0].replace("];","]"))
                current_results_len = len(loc)
                for val in loc:
                    store = []
                    store.append(base_url)
            
                    additional =''
                    if "additional" in  val['location'] and val['location']['additional'] != None:
                        additional = val['location']['additional']
                    city = val['location']['city']
                    
                    for data in val['location']['entities']:
                        if "name" in data:
                            location_name  = data['name']
                        location_type  = data['type']
                        phone = data['phone']
                        drive1 = ''
                        lobby1 = ''
                        if data['open_hours_formatted'] != {}:
                            if "drive" in data['open_hours_formatted']:
                                listOfStr = data['open_hours_formatted']['drive']
                                listOfStr1 = ['Sunday','Monday', "Tuesday",'Wednesday','Thursday',"Friday","Saturday"]
                                dictOfWords = { listOfStr1[i] : listOfStr[i] for i in range(len(listOfStr1))}
                                drive =''
                                for data2 in dictOfWords:
                                    drive = drive +' ' +data2 +' '+ str(dictOfWords[data2])
                                drive1 = 'Drive Through' + drive
                        

                            if "lobby" in data['open_hours_formatted']:
                                listOfStr = data['open_hours_formatted']['lobby']
                                listOfStr1 = ['Sunday','Monday', "Tuesday",'Wednesday','Thursday',"Friday","Saturday"]
                                dictOfWords = { listOfStr1[i] : listOfStr[i] for i in range(len(listOfStr1))}
                                lobby =''
                                for data1 in dictOfWords:
                                    lobby = lobby +' ' +data1 +' '+ str(dictOfWords[data1])
                                lobby1 = ' lobby ' + lobby
                        
                    hours_of_operation =drive1 + ' ' + lobby1
                    store.append(location_name if location_name else "<MISSING>")
                    store.append(val['location']['street']+' '+additional)
                    store.append(city)
                    store.append(val['location']['province'])
                    if val['location']['postal_code'] != None:
                        store.append(val['location']['postal_code'])
                    else:
                        store.append("<MISSING>")
                    store.append(val['location']['country'])
                    store.append(val['location']['id'])
                    store.append(phone if phone else "<MISSING>")
                    store.append(location_type if location_type else "<MISSING>")
                    store.append(val['location']['lat'])
                    store.append(val['location']['lng'])
                    result_coords.append((val['location']['lat'], val['location']['lng']))
                    store.append(hours_of_operation.strip().lstrip() if hours_of_operation.strip().lstrip() else "<MISSING>")
                    store.append("<MISSING>")
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    yield store
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
