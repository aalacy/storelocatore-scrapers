import csv
import requests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json
import  pprint
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
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
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
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
    base_url = "https://www.windowworld.com"

    headers = {
        'authorization': "R8-Gateway App=shoplocal, key=guess, Type=SameOrigin",
        'cache-control': "no-cache"
    }
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 200
    coords = search.next_coord()
    current_results_len = 0
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
    while coords:

            result_coords = []
            # print("zip_code === " + str(coords))
            #print("ramiang zip =====" + str(search.current_zip))
            
            r = request_wrapper("https://www.windowworld.com/store-locator?zip="+str(search.current_zip)+"&county=",'get', headers=header)
            if r == None:
                search.max_distance_update(MAX_DISTANCE)
                coords = search.next_zip()
                continue
            soup = BeautifulSoup(r.text, "lxml")
            current_results_len =len(soup.find_all("a",{"title":re.compile("Visit Store Profile")}))

            for val in  soup.find_all("a",{"title":re.compile("Visit Store Profile")}):
                page_url = val['href']
                r = request_wrapper(val['href'],'get',headers=header)
                if r == None:
                    continue
                soup = BeautifulSoup(r.text, "lxml")
                pera  = soup.find('script',{'async':'','type':'text/javascript'})['src'].split('&')
                
                api_key  = pera[0].split('?')[1].replace('key=','').strip()
                account_id  = pera[1].replace('account_id=','')
                location_id  = pera[2].replace('location_id=','')
                url = "https://knowledgetags.yextpages.net/embed?key="+str(api_key)+"&account_id="+str(account_id)+"&location_id="+str(location_id)
                r = request_wrapper(url,'get', headers=header)
                if r == None:
                    continue
                k = json.loads(r.text.split(';})();')[1].strip().replace('Yext._embed(','').replace(')','').replace('@',''))

                data = k['entities']
                # print(data)
                for id,val in enumerate(data):
                    locator_domain = base_url
                    location_name = val['attributes']['locationName'].strip()
                    street_address = val['attributes']['address'].strip()
                    city = val['attributes']['city']
                    state = val['attributes']['isoRegionCode']
                    zip =  val['attributes']['zip']
                    country_code = val['attributes']['countryCode']
                    store_number = ''
                    phone = val['attributes']['phone'].replace('(','')
                    location_type = ''
                    latitude = val['attributes']['yextDisplayLat']
                    longitude = val['attributes']['yextDisplayLng']
                    result_coords.append((latitude,longitude))
                    hours_of_operation = ''
                    if 'openingHoursSpecification' in val['schema']:
                        hour = val['schema']['openingHoursSpecification']
                        jk = []
                        dayOfWeek = opens = closes = ''
                        for z in hour:
                            if 'dayOfWeek' in z:
                                dayOfWeek =  z['dayOfWeek']
                            if 'opens' in z:
                                opens =  z['opens']
                            if 'closes' in z:
                                closes = z['closes']
                            jk.append(dayOfWeek + " opens " + opens + "  closes " + closes)

                        hours_of_operation = ' '.join(jk)
                    if street_address in addresses:
                        continue
                    addresses.append(street_address)
                    # page_url = val['href']
                    store = []
                    store.append(locator_domain if locator_domain else '<MISSING>')
                    store.append(location_name if location_name else '<MISSING>')
                    store.append(street_address if street_address else '<MISSING>')
                    store.append(city if city else '<MISSING>')
                    store.append(state if state else '<MISSING>')
                    store.append(zip if zip else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                    store.append(page_url if page_url else '<MISSING>')
                    #print("===", str(store))
                    yield store

            # if current_results_len < MAX_RESULTS:
            #     print("max distance update")
            #     search.max_distance_update(MAX_DISTANCE)
            if current_results_len < MAX_RESULTS:
                #print("max count update")
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")

            coords = search.next_zip()
        # break

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
