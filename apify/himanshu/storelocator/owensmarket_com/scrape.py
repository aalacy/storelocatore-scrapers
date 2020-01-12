import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import phonenumbers
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url, headers=headers, data=data)
                else:
                    r = requests.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0    
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while zip_code:
        result_coords = []
        location_name = ""
        street_address = ""
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
        base_url = "https://www.owensmarket.com"
        location_url= "https://www.owensmarket.com/stores/search?searchText="+str(zip_code)
        r = request_wrapper(location_url,'get',headers=headers)
        # r = requests.get(location_url, headers=headers)
        soup= BeautifulSoup(r.text,"lxml")
        script = soup.find(lambda tag: (tag.name == "script") and "window.__INITIAL_STATE__" in tag.text).text
        str_json = script.split("JSON.parse('")[1].split("')")[0].replace("\\","\\\\")
        s = json.loads(re.sub(r"\s+", " ",str_json))
        if 'stores' in s['storeSearch']['storeSearchReducer']['searchResults'] :
            for i in s['storeSearch']['storeSearchReducer']['searchResults']['stores']:           
                location_name = (i['vanityName'])
                store_number = i['storeNumber']               
                latitude = i['latitude']       
                longitude = i['longitude']            
                street_address = (str(i['address']['addressLine1'])+" "+str(i['address']['addressLine2']))            
                city = (i['address']['city'])            
                zipp = (i['address']['zip'])           
                state = (i['address']['stateCode'])    
                if i['phoneNumber']:
                    phone = phonenumbers.format_number(phonenumbers.parse(i['phoneNumber'], 'US'), phonenumbers.PhoneNumberFormat.NATIONAL) 
                else:
                    phone = "<MISSING>"
                page_url = "https://www.owensmarket.com/stores/details/"+str(i['divisionNumber'])+"/"+str(store_number)
                hours_of_operation = ''
                for k in i['ungroupedFormattedHours']:
                    hours_of_operation = hours_of_operation +' '+k['displayName']+' '+k['displayHours']
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append(store_number if store_number else "<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("Store")
                store.append( latitude if latitude else "<MISSING>")
                store.append( longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
        try:
            r1 = requests.get(location_url, headers=headers)
        except:
            pass
        soup1= BeautifulSoup(r1.text,"lxml")
        script = soup1.find(lambda tag: (tag.name == "script") and "window.__INITIAL_STATE__" in tag.text).text
        str_json = script.split("JSON.parse('")[1].split("')")[0].replace("\\","\\\\")
        s = json.loads(re.sub(r"\s+", " ",str_json))
        if 'fuel' in s['storeSearch']['storeSearchReducer']['searchResults'] :
            for i in s['storeSearch']['storeSearchReducer']['searchResults']['fuel']:       
                location_name = (i['vanityName'])
                store_number = i['storeNumber']               
                latitude = i['latitude']       
                longitude = i['longitude']            
                street_address = (str(i['address']['addressLine1'])+" "+str(i['address']['addressLine2']))            
                city = (i['address']['city'])            
                zipp = (i['address']['zip'])           
                state = (i['address']['stateCode'])    
                if i['phoneNumber']:
                    phone = phonenumbers.format_number(phonenumbers.parse(i['phoneNumber'], 'US'), phonenumbers.PhoneNumberFormat.NATIONAL) 
                else:
                    phone = "<MISSING>"
                page_url = "https://www.owensmarket.com/stores/details/"+str(i['divisionNumber'])+"/"+str(store_number)
                hours_of_operation = ''
                if i['ungroupedFormattedHours']:
                    for k in i['ungroupedFormattedHours']:
                        hours_of_operation = hours_of_operation +' '+k['displayName']+' '+k['displayHours']
                else:
                    hours_of_operation = "<MISSING>"
                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append(store_number if store_number else "<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("Fuel")
                store.append( latitude if latitude else "<MISSING>")
                store.append( longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
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
