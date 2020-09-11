import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

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
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
    }

    base_url = "https://www.menswearhouse.com"

    while zip_code:
        result_coords = []

        #print("zip_code === "+zip_code)
        # data = '{"request":{"appkey":"9E9DE426-8151-11E4-AEAC-765055A65BB0","formdata":{"geoip":false,"dataview":"store_default","geolocs":{"geoloc":[{"addressline":"'+str(zip_code)+'","country":"US","latitude":"","longitude":""}]},"searchradius":"10|20|50|100","where":{"nci":{"eq":""},"and":{"PROPANE":{"eq":""},"REDBOX":{"eq":""},"RUGDR":{"eq":""},"MULTICULTURAL_HAIR":{"eq":""},"TYPE_ID":{"eq":""},"DGGOCHECKOUT":{"eq":""},"FEDEX":{"eq":""},"DGGOCART":{"eq":""}}},"false":"0"}}}'
        
        
        location_url = "https://www.menswearhouse.com/sr/search/resources/store/12751/storelocator/byProximity?radius="+str(MAX_DISTANCE)+"&zip="+str(zip_code)+"&city=&state=&brand=TMW&profileName=X_findStoreLocatorWithExtraFields"
        try:
            loc = session.get(location_url,headers=headers).json()
        except:
            continue
        # soup1 = BeautifulSoup(loc.text, "html.parser")
        
 
        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")

               # it always need to set total len of record.

        locator_domain = base_url
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
        street_address1 = ''
        street_address2 = ''
        store_name=''
        # print("location_url ==== ",loc['collection'])
        if "DocumentList" in loc:
            current_results_len = len(loc['DocumentList']) 
            
            for data in loc['DocumentList']:
                store_name = data['storeName']
                if "address1_ntk" in data:
                    street_address1 = data['address1_ntk']
                
                if "address2_ntk" in data:
                    street_address2 = data['address2_ntk']
                
                
                street_address = street_address1+ ' '+street_address2
             
           
                soup = BeautifulSoup(data['working_hours_ntk'], "lxml")

                hours_of_operation =  " ".join(list(soup.stripped_strings)).lower().replace("pm"," pm ").replace("am",' am ').replace("sun"," sun ").replace("mon"," mon ").replace("wed"," wed ").replace("thu"," thu ").replace("fri"," fri ").replace("sat"," sat ").replace("tue"," tue ")
                # print(hours_of_operation)
    
                # do your logic.
                page_url = "https://www.menswearhouse.com/store-locator/"+str(data['stloc_id'])
                store_number = str(data['stloc_id'])
                result_coords.append((latitude, longitude))
                if "phone_ntk" in data:
                    phone =data['phone_ntk']
                else:
                    phone = "<MISSING>"
                
                # street_address = street_address.replace(store_name,'')
                store = [locator_domain, store_name.capitalize(), street_address.replace(data['state_ntk'],"").lower(), data['city_ntk'].lower(), data['state_ntk'], data['zipcode_ntk'], country_code,
                        store_number, phone, location_type, data['latlong'].split(",")[0], data['latlong'].split(",")[1], hours_of_operation,page_url]

                if store[2] + store[-3] in addresses:
                    continue

                addresses.append(store[2] + store[-3])
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                yield store
            # return_main_object.append(store)

        # yield store
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
