import csv
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('oritani_com')




# def request_wrapper(url,method,headers,data=None):
#    request_counter = 0
#    if method == "get":
#        while True:
#            try:
#                r = requests.get(url,headers=headers)
#                return r
#                break
#            except:
#                time.sleep(2)
#                request_counter = request_counter + 1
#                if request_counter > 10:
#                    return None
#                    break
#    elif method == "post":
#        while True:
#            try:
#                if data:
#                    r = requests.post(url,headers=headers,data=data)
#                else:
#                    r = requests.post(url,headers=headers)
#                return r
#                break
#            except:
#                time.sleep(2)
#                request_counter = request_counter + 1
#                if request_counter > 10:
#                    return None
#                    break
#    else:
#        return None


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
    MAX_RESULTS = 1000
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    result_len=0
    base_url = "https://www.oritani.com"
    
    while zip_code:
        result_coords =[]
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        url = "https://www.valley.com/siteAPI/Branch/Branches"

        payload = "{\"Location\":\"'"+str(zip_code)+"'\"}"
        # logger.info(payload)
        headers = {
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Content-Length': '20',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.valley.com',
        'Referer': 'https://www.valley.com/find-a-branch',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        }
        try:
            json_data = requests.request("POST", url, headers=headers, data = payload).json()
        except:
            continue
        # if "Branches" in json_data:
        #     json_data = len(json_data['Branches'])
        # logger.info(json_data)
        if type(json_data)==str:
            data = json.loads(json_data)
            if 'Branches' in data:
                result_len = len(data['Branches'])
                for store in data['Branches']:
                    location_name = store['Name']
                    street_address = store['StreetAddress']
                    city = store['City']
                    state = store['State']
                    zipp = store['Zipcode']
                    phone = store['PhoneFormatted']
                    lat = store['Lat']
                    lng = store['Lng']
                    store_number = store['ID']
                    location_type = store['Type']
                    page_url = "https://www.valley.com"+store['Path'].lower()
                    hours = ""
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
                    try:    
                        store_soup = bs(requests.get(page_url).text,'lxml')
                    except:
                        continue
                    
                    hours=''
                    names_hours = (store_soup.find_all("a",{"href":re.compile("#panel")}))
                    for index,i in enumerate(store_soup.find_all("div",{"id":"panel1"})):
                        if i['id']==names_hours[index]['href'].replace("#",''):
                            hours = hours + ' '+names_hours[index].text.strip().replace("Lobby","") + ' '+" ".join(list(i.stripped_strings))
                    # logger.info(hours)
                    # hours = " ".join(list(store_soup.find("div",{"class":"tabs-content","class":"small-9"}).stripped_strings))
                    # try:
                    # store_soup = request_wrapper(page_url,"get",headers=headers)
                    # except:
                    #     pass
                    result_coords.append((lat,lng))
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
                    store.append(location_type)
                    store.append(lat)
                    store.append(lng)
                    store.append(hours if hours else "<MISSING>")
                    store.append(page_url)     
                    if store[2] in adressess:
                        continue
                    adressess.append(store[2]) 
                    store = [str(x).strip() if x else "<MISSING>" for x in store]
                    yield store
                    #logger.info(store)
             
        if (result_len) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif (result_len) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
