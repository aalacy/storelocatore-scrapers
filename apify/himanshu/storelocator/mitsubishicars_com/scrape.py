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
    base_url ="https://www.mitsubishicars.com"
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    addressess =[]
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    while zip_code:
        result_coords = []
        try:
            r=requests.get('https://www.mitsubishicars.com/rs/dealers?bust=1569242590201&zipCode='+str(zip_code)+'&idealer=false&ecommerce=false').json()
        except:
            continue
        hours_of_operation = '' 
        current_results_len = len(r)  
        for loc in r:
            if loc['zipcode']:
                link = loc['dealerUrl'] 
                if link != None:
                    page_url = "http://"+link.lower()
                    try:
                        r=requests.get(page_url)
                    except:
                        continue
                    soup = BeautifulSoup(r.text, "lxml")
                    main=soup.find('h3',text=re.compile("Hours"))
                    if main != None:
                        if main.parent != None:
                            hours_of_operation = " ".join(list(main.parent.stripped_strings))
                # page_url = 
                address=loc['address1'].strip()
                if loc['address2']:
                    address+=' '+loc['address2'].strip()
                name=loc['dealerName'].strip()
                city=loc['city'].strip()
                state=loc['state'].strip()
                zip=loc['zipcode']
                phone=loc['phone'].strip()
                country=loc['country'].strip()
                if country=="United States":
                    country="US"
                lat=loc['latitude']
                lng=loc['longitude']
                hour=''
                storeno=loc['bizId']
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
                store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
                store.append(page_url)
                #print(store)
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
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

           
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
