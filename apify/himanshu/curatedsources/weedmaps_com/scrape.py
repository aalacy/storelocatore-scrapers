import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from random import choice
import html5lib


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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    addresses = []
    page = 1
    base_url = "https://weedmaps.com/"
    while True:
        
        r1 = proxy_request('get',"https://api-g.weedmaps.com/discovery/v1/listings?page_size=150&page="+str(page)+"&filter%5Bany_retailer_services%5D%5B%5D=storefront&filter%5Bbounding_box%5D=-4.089616869799286%2C-166.57642364501956%2C67.35440609528173%2C-56.97681427001954", headers=headers)
        if r1 == None:
            continue
        try:
            location_list = r1.json()["data"]["listings"]
        except:
            continue
        
        if location_list == []:
            break
        for weed in location_list:
            #print("page number is=========="+str(page))
            location_name = weed['name'].encode('ascii', 'ignore').decode('ascii').strip()
            if "Coming Soon" in location_name:
                continue
            street_address = weed['address']
            city = weed['city']
            state = weed['state']
            zipp = weed['zip_code']
            if len(zipp) == 5:
                country_code = "US"
            else:
                country_code = "CA"
            store_number = weed['id']
            latitude = weed['latitude']
            longitude = weed['longitude']
            location_type = weed['type']
            page_url = weed['web_url']+"/about"
            r = requests.request('get',page_url, headers=headers)
            if r == None:
                continue
            soup = BeautifulSoup(r.text, "lxml")
            if soup.find("div",{"class":re.compile("components__OpenHours")}):
                hours = " ".join(list(soup.find("div",{"class":re.compile("components__OpenHours")}).stripped_strings)).replace("Closed Now","")
            else:
                hours = "<MISSING>"
            
            if soup.find("div",{"class":"src__Box-sc-1sbtrzs-0 styled-components__DetailGridItem-d53rlt-0 styled-components__PhoneNumber-d53rlt-8 cMfVkr"}):
                phone = soup.find("div",{"class":"src__Box-sc-1sbtrzs-0 styled-components__DetailGridItem-d53rlt-0 styled-components__PhoneNumber-d53rlt-8 cMfVkr"}).text.replace("-STOP ","-").replace("Coming Soon","<MISSING>")
            else:
                phone = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code)
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            #print("data ======="+str(store))
            yield store
        
        page += 1
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
