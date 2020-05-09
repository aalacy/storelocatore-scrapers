# coding=UTF-8
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
def getDecodedPhoneNo(encoded_phone_no):
    _dict = {}
    _dict["2"] = "ABC"
    _dict["3"] = "DEF"
    _dict["4"] = "GHI"
    _dict["5"] = "JKL"
    _dict["6"] = "MNO"
    _dict["7"] = "PQRS"
    _dict["8"] = "TUV"
    _dict["9"] = "WXYZ"

    _real_phone = ""
    for _dg in encoded_phone_no:
        for key in _dict:
            if _dg in _dict[key]:
                _dg = key
        _real_phone += _dg
    return _real_phone

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ['us', 'ca'])
    MAX_RESULTS = 150
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.

    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while zip_code:
        result_coords = []
        #print("zip_code === "+zip_code)
        base_url=  "https://www.orangetheoryfitness.com/service/directorylisting/filterMarkers?s="+str(zip_code)
        try:
            r = session.get(base_url)
            json_data = r.json()
        except:
            pass
        
        # print(len(json_data['markers']))
        current_results_len= len(json_data['markers'])
        for i in json_data['markers']:
            hours_of_operation="<MISSING>"
            store_number = i['id']
            location_name = i['name']
            street_address = i['address1']
            street_address1=i['address2']
            try:
                if street_address1 != None:
                    street_address1 = street_address1
                else:
                    street_address1=''
            except:
                street_address1=''
            
            if street_address == None:
                street_address = "<MISSING>"


            city = i['city']
            state = i['state']
            zipp = i['zip'].replace("0209","80209").replace("880209","80209").replace("2550","12550").replace("125504","25504").replace("2145","02145").encode('ascii', 'ignore').decode('ascii').strip()
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            phone = getDecodedPhoneNo(i['phone']).replace("08837","<MISSING>").replace("(2683)","").encode('ascii', 'ignore').decode('ascii').strip()
            latitude  = i['lat']
            longitude = i['lon']
            page_url = i['web_site']
            try:
                r1 = session.get(page_url)
                soup1 = BeautifulSoup(r1.text,"lxml")
                try:
                    hours_of_operation =json.loads(soup1.find("script",{"type":"application/ld+json"}).text)['openingHours']
                except:
                    hours_of_operation="<MISSING>"
            except:
                hours_of_operation="<MISSING>"

            if "Wichita West" in location_name:
                street_address = "2835 N Maize Rd., Suite 161"
            result_coords.append((latitude, longitude))
            store = []
            store.append("https://www.orangetheoryfitness.com/")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address+' '+street_address1 if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp)
            store.append(country_code)
            store.append(store_number.replace("37630","") if store_number else "<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            if "Adjuntas" in store :
                pass
            else:
                yield store
            # print("--------------------",store)
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
