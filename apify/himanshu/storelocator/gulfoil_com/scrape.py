import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    base_url = "http://gulfoil.com"


    while zip_code:
        location_name = ""
        street_address1 = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ''
        #print(zip_code)
        result_coords = []
        q = 0
        is_true = True
        while is_true:
            json_data = requests.post("http://gulfoil.com/views/ajax?view_name=station_locator_block&view_display_id=block&field_geofield_distance%5Bdistance%5="+str(MAX_DISTANCE)+"&D=1000000&field_geofield_distance%5Borigin%5D="+str(zip_code)+"&page="+str(q),
                            headers=header).json()
            for loc in json_data:
                if "data" in loc:
                    soup = BeautifulSoup(loc['data'], "lxml")
                    # print("qqqqq",q)
                    table1 = soup.find('table',{'class':'table'})
                    if table1==None:
                        is_true =False
                    else:
                        table = soup.find_all('table',{'class':'table'})
                        current_results_len = len(table)
                        for i in range(len(table)):
                            location_name  = table[i].find("span").text
                            address_tage = table[i].find("p")
                            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(table[i]))
                            if phone_list:
                                phone = phone_list[-1]

                            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address_tage.text))
                            if us_zip_list:
                                zipp = us_zip_list[-1]
                                country_code = "US"

                            state_list = re.findall(r' ([A-Z]{2})', str(address_tage.text))


                            if state_list:
                                state = state_list[-1]

                            full_address = list(address_tage.stripped_strings)
                            
                                
                            indices = [i for i, s in enumerate(full_address) if zipp in s]
                            city = full_address[indices[0]].replace(state,"").replace(zipp,"").replace(",",'').strip()
                            if indices and indices[0]>0:
                                street_address = " ".join(full_address[:indices[0]])
                            else:
                                street_address = "<MISSING>"
                
                            # print("==========================full_address=  ",full_address)
                            # print("==========================city=  ",city)
                            # print(indices[0],"==========================street_address=  ",street_address)
                            store = []
                            locator_domain =base_url
                            result_coords.append((latitude, longitude))
                            store.append(locator_domain if locator_domain else '<MISSING>')
                            store.append(location_name if location_name else '<MISSING>')
                            store.append(street_address if street_address else '<MISSING>')
                            store.append(city if city else '<MISSING>')
                            store.append(state if state else '<MISSING>')
                            store.append(zipp if zipp else '<MISSING>')
                            store.append(country_code if country_code else '<MISSING>')
                            store.append(store_number if store_number else '<MISSING>')
                            store.append(phone if phone else '<MISSING>')
                            store.append(location_type if location_type else '<MISSING>')
                            store.append(latitude if latitude else '<MISSING>')
                            store.append(longitude if longitude else '<MISSING>')
                            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                            store.append("<MISSING>")
                            if store[2] in addressess:
                                continue
                            addressess.append(store[2])
                            #print('---store--'+str(store))
                            yield store
                    
            q= q+1
        if current_results_len < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()           
        #print("===========================================", q)
            

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
