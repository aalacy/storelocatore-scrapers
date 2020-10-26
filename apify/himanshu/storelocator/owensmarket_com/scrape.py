import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import phonenumbers


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 70
    MAX_DISTANCE = 50
    current_results_len = 0     
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while zip_code:
        result_coords = []
        base_url = "https://www.owensmarket.com"
        location_url= "https://www.owensmarket.com/stores/search?searchText="+str(zip_code)
        try:
            r = session.get(location_url, headers=headers)
        except:
            pass
        soup= BeautifulSoup(r.text,"lxml")
        # print(soup)
        script = soup.find(lambda tag: (tag.name == "script") and "window.__INITIAL_STATE__" in tag.text).text
        str_json = script.split("JSON.parse('")[1].split("')")[0].replace("\\","\\\\").split('"contentHash":"W/\\')[0].replace('"/"}]}},','"/"}]}}}}}')
        # print(str_json)
        s = json.loads(re.sub(r"\s+", " ",str_json))
        # print(s)
        if 'stores' in s['storeSearch']['storeSearchReducer']['searchResults']:
            for i in s['storeSearch']['storeSearchReducer']['searchResults']['stores']:
                # print(i)
                location_name = (i['vanityName'])
                store_number = i['storeNumber']
                latitude = i['latitude']
                longitude = i['longitude']
                street_address = (str(i['address']['addressLine1'])+" "+str(i['address']['addressLine2']).replace("None",""))
                city = (i['address']['city'])
                zipp = (i['address']['zip'])
                state = (i['address']['stateCode'])
                # print(state)
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
                store.append("store")
                store.append( latitude if latitude else "<MISSING>")
                store.append( longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                # print(str(store))
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
        try:
            r1 = session.get(location_url, headers=headers)
        except:
            pass
        soup1= BeautifulSoup(r1.text,"lxml")
        script = soup1.find(lambda tag: (tag.name == "script") and "window.__INITIAL_STATE__" in tag.text).text
        str_json1 = script.split("JSON.parse('")[1].split("')")[0].replace("\\","\\\\").split('"contentHash":"W/\\')[0].replace('"/"}]}},','"/"}]}}}}}')
        # print(str_json1)
        s1 = json.loads(re.sub(r"\s+", " ",str_json1))
        # print(s1)
        if 'fuel' in s1['storeSearch']['storeSearchReducer']['searchResults']:
            for i in s1['storeSearch']['storeSearchReducer']['searchResults']['fuel']:
                location_name = (i['vanityName'])
                store_number = i['storeNumber']
                latitude = i['latitude']
                longitude = i['longitude']
                street_address = (str(i['address']['addressLine1'])+" "+str(i['address']['addressLine2']).replace("None",""))
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
                store.append("fuel")
                store.append( latitude if latitude else "<MISSING>")
                store.append( longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # print(str(store))
                yield store
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")                                                                        
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # break
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
