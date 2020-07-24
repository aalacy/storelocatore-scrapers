import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
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
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    base_url = "http://cashamerica.com/cashland"
    link = "http://find.cashamerica.us/api/stores?p=1&s=1259&lat=33.5973&lng=-112.1073&d=2020-03-18T12:13:28.997Z&key=D21BFED01A40402BADC9B931165432CD"
    r = session.get(link,headers=headers)
    json_data = r.json()
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    for location in json_data:
        distance = location['distance']
        h = location['hours']['openTime']
        status =location['hours']['storeStatus']
        store_number =  str(location['storeNumber'])
        location_type = location['brand']
      #  print(location_type)
        page_url = "http://find.cashamerica.us/#/storesdetails/"+store_number+'/'+location_type+'/'+str(distance)+'/'+h+'/'+status
        http = "http://find.cashamerica.us/api/stores/"+str(store_number)+"?key=D21BFED01A40402BADC9B931165432CD"
        all_data = session.get(http, headers=headers).json()
        location_name = location['brand']
        street_address = all_data['address']['address1']
        city = all_data['address']['city']
        state = all_data['address']['state']
        US_State = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH",'OK',"OR","PA","RI","SC","SD",'TN',"TX","UT","VT","VA","WA","WV","WI","WY"]
 
        if state not in US_State:
            continue
        zipp = all_data['address']['zipCode']
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
        state_list = re.findall(r' ([A-Z]{2}) ', str(zipp))
        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"
        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        latitude = str(location['latitude'])
        longitude = str(location['longitude'])
        phone = all_data['phone']
        # print(all_data)
        # exit()
        hours_of_operation1 ='' 
        if "weeklyHours" in all_data:
            hours_of_operation = all_data['weeklyHours']
            for i in hours_of_operation:
                hours_of_operation1 = hours_of_operation1 +' ' +(i['weekDay'] + ' ' + i['openTime'] + ' ' +i['closeTime'])
        else:
            hours_of_operation = '<MISSING>' 
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    str(store_number), str(phone), location_type.replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","").replace("#","").strip(), str(latitude), str(longitude), hours_of_operation1,page_url.replace(" ","%20")]
        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
