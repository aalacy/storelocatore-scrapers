import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import html5lib
import pprint
from random import randrange
from random import choice
import unicodedata


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def get_proxy():
    url = "https://www.sslproxies.org/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html5lib")
    return {'https': (choice(list(map(lambda x:x[0]+':'+x[1],list(zip(map(lambda x:x.text,soup.findAll('td')[::8]),map(lambda x:x.text,soup.findAll('td')[1::8])))))))}

    
def proxy_request(request_type, url, **kwargs):
    while 1:
        try:
            proxy = get_proxy()
            # print("Using Proxy {}".format(proxy))
            r = requests.request(request_type, url, proxies=proxy, timeout=5, **kwargs)
            break
        except:
            pass
    return r


def fetch_data():
    headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,gu;q=0.8',
    'Connection': 'keep-alive',
    'Host':'bellca.know-where.com',
    'Origin': 'https://www.bell.ca',
    'Referer': 'https://www.bell.ca/Store_Locator',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["CA"])
    MAX_RESULTS = 25
    MAX_DISTANCE = 75.0
    coord = search.next_coord()
    while coord:
        result_coords = []
        x = coord[0]
        y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r = proxy_request("get","https://bellca.know-where.com/bellca/cgi/selection?lang=en&loadedApiKey=main&ll="+str(x)+"%2C"+str(y)+"&stype=ll&async=results&key", headers=headers)

        soup = BeautifulSoup(r.text,"lxml")
        data = soup.find_all("script", {"type":"application/ld+json"})
        hours = soup.find_all("ul", {"class":"rsx-sl-store-list-hours"})
        hours1 = []
        for time in hours:
            hours1.append(' '.join(list(time.stripped_strings)).replace(" ","").replace("p.m.","p.m. ").replace("Closed","Closed "))
     
        lat = r.text.split("poilat")[1].split(",")[0].replace('"',"").replace(":","")
        lng = r.text.split("poilon")[1].split(",")[0].replace('"',"").replace(":","")
        for index,i in enumerate(data):
            json_data = json.loads(i.text)
            street_address = json_data['address']['streetAddress']
            city = json_data['address']['addressLocality']
            state = json_data['address']['addressRegion']
            zipp = json_data['address']['postalCode']
            location_name = json_data['name']
            phone = json_data['telephone']
            
            result_coords.append((lat,lng))
            store = []
            store.append("https://www.bell.ca")
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append("CA")
            store.append('<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append(hours1[index])
            store.append("<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            if adrr not in output:
                output.append(adrr)
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("\xe2","-") if type(x) == str else x for x in store]
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]          
            yield store   
        if len(data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
