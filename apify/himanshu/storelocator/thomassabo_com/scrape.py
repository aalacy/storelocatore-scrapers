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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.thomassabo.com"
    return_main_object=[]
    addresses=[]
    cord=sgzip.coords_for_radius(100)
    for cr in cord:
        try:
            r = requests.get(base_url+"/on/demandware.store/Sites-TS_US-Site/en_US/Shopfinder-GetStores?searchMode=radius&searchPhrase=&searchDistance=4934.527951623432&lat="+cr[0]+"&lng="+cr[1]+"&filterBy=").json()
            # print(base_url+"/on/demandware.store/Sites-TS_US-Site/en_US/Shopfinder-GetStores?searchMode=radius&searchPhrase=&searchDistance=4934.527951623432&lat="+cr[0]+"&lng="+cr[1]+"&filterBy=")

            for loc in r:
                # print(loc)
                if "address1" in loc and "stateCode" in loc:
                    zip=''
                    # if "postalCode" in loc:
                        # zip=loc['postalCode'].strip()
                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(loc['postalCode']))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(loc['postalCode']))

                    if ca_zip_list:
                        zip = ca_zip_list[0]
                        country = "CA"
                    elif us_zip_list:
                        zip = us_zip_list[0]
                        country = "US"
                    else:
                        continue

                    name=loc['name'].capitalize().strip()
                    address=loc['address1'].capitalize().strip()
                    city=loc['city'].strip()
                    state=loc['stateCode']
                    # zip=''
                    # if "postalCode" in loc:
                    #     zip=loc['postalCode'].strip()
                    # if len(zip)==4:
                    #     zip=str(0)+zip
                    phone=''
                    if "phone" in loc:
                        phone=loc['phone'].strip()

                    storeno=loc['ID'].strip()
                    lat=loc['latitude']
                    lng=loc['longitude']
                    page_url = "<MISSING>"
                    hour = ''
                    store=[]
                    store.append(base_url)
                    store.append(name if name else "<MISSING>")
                    store.append(address if address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zip if zip else "<MISSING>")
                    store.append(country if country else "<MISSING>")
                    store.append(storeno if storeno else "<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour if hour.strip() else "<MISSING>")
                    store.append(page_url if page_url else "<MISSING>")

                    adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
                    if store[2]  in addresses:
                        continue
                    addresses.append(store[2])
                    # print('zipp == '+zip)
                    return_main_object.append(store)
                    print("data===="+str(store))
                    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        except:
            continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
