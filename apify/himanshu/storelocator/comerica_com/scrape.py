import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import re
import json
import sgzip
# from tenacity import *
# import timeout_decorator


session = SgRequests()

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    base_url = "https://www.comerica.com"

    while zip_code:
        result_coords = []
        page = 1
        while True:
            
            r = session.get("https://locations.comerica.com/?q="+str(zip_code)+"&filter=all&page="+str(page))
            soup = BeautifulSoup(r.text, "lxml")
            data = soup.find(lambda tag: (tag.name == "script") and "var results" in tag.text)
            if data:
                json_data = json.loads(data.text.split('var results = ')[1].split('var map;')[0].replace("];","]"))
                current_results_len = len(json_data)
                for i in json_data:
                    if i['location']['alias'] == None:
                        continue
                    page_url = "https://locations.comerica.com/location/"+str(i['location']['alias'])
                    # print(page_url)
                    street_address = (i['location']['street'] +" "+ str(i['location']['additional'])).replace("None","").strip()
                    city = i['location']['city']
                    state = i['location']['province']
                    zipp = i['location']['postal_code']
                    country_code = i['location']['country']
                    store_number = i['location']['id']
                    location_type = "/".join(i['location']['m_entity_types'])
                    latitude = i['location']['lat']
                    longitude = i['location']['lng']

                    r1 = session.get(page_url)
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    if soup1.find("h4",{"property":"name"}):
                        location_name = soup1.find("h4",{"property":"name"}).text.strip()
                    else:
                        location_name = "<MISSING>"
                    if soup1.find("span",{"property":"telephone"}):
                        phone = soup1.find("span",{"property":"telephone"}).text.strip()
                    else:
                        phone = "<MISSING>"
                    hours = soup1.find_all("div",{"class":"col-xs-4"})
                    if hours != []:
                        if len(hours) == 6 or len(hours) == 7:
                            hours_of_operation = " ".join(list(soup1.find_all("div",{"class":"col-xs-4"})[0].stripped_strings)) +" "+ \
                            " ".join(list(soup1.find_all("div",{"class":"col-xs-4"})[1].stripped_strings))
                        elif len(hours) == 5:
                        
                            hours_of_operation = " ".join(list(soup1.find_all("div",{"class":"col-xs-4"})[0].stripped_strings))
                        else:
                            if "Monday" in soup1.find_all("div",{"class":"col-xs-4"})[0].text:
                                hours_of_operation = " ".join(list(soup1.find_all("div",{"class":"col-xs-4"})[0].stripped_strings))
                            else:
                                hours_of_operation = "<MISSING>"   
                    else:
                        hours_of_operation = "<MISSING>"
                    
                    result_coords.append((latitude,longitude))
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append(country_code)
                    store.append(store_number) 
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation.replace('PM','PM,'))
                    store.append(page_url)

                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    # print("data ===="+str(store))
                    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

                    yield store 

            else:
                break
            page+=1

                
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
