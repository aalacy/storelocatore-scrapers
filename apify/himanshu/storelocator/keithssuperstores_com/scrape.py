from sgrequests import SgRequests
from bs4 import BeautifulSoup 
import csv
import re
import json
from itertools import groupby
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('keithssuperstores_com')


session = SgRequests()

def merge(d1, d2): 
      
    merged_list = [(d1[i], d2[i]) for i in range(0, len(d1))] 
    return merged_list
def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    base_url = "http://www.keithssuperstores.com"
    locator_domain = base_url

    page_url = "http://www.keithssuperstores.com/store-location"

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'method': 'GET',
    }
    addresses = []
    r = session.get(page_url, headers=headers)

    soup = BeautifulSoup(r.text,"lxml")
    info = []
    for data1 in soup.find("div",{"class":"u_1641317848 dmNewParagraph"}):
        

        for br in data1.find_all("br"):
            br.replace_with("|")
        info.append(data1.text)
    loc_list = " ; ".join(info).split("|")
    d =[]
    for i in loc_list:
        loc = i.split("Food Shop")[0].split(" ; ")
        loc = [el.replace('\xa0','') for el in loc]
        loc = [x for x in loc if x != '']
        
        if loc == []:
            continue
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(loc[0]))
        if len(loc) >= 4 and us_zip_list == []:
            
            location_name = loc[0].strip()
            address = loc[1].split(",")
            if len(address) > 2:
                street_address = address[0]
                city = address[1]
                state = address[-1].split()[0]
                zipp = address[-1].split()[-1]
            else:
                street_address = address[0]
                city= address[-1].split()[0]
                state =address[-1].split()[1] 
                zipp =address[-1].split()[-1] 
            
            phone = loc[2].replace("Phone:","").strip()
            hours_of_operation = "  ".join(loc[3:]).replace("Hours:","").strip()
            latitude    = "<MISSING>"
            longitude = "<MISSING>"
            store_number = "<MISSING>"
            location_type = location_name.split("Superstores")[1].replace("-","").replace("–","").strip()
                
            country_code = "US"
            store = [locator_domain, location_name,street_address, city, state, zipp, country_code,store_number, phone, location_type if location_type else "<MISSING>", latitude, longitude, hours_of_operation, page_url]
            
            if str(store[2]) not in addresses:
                addresses.append(str(store[2]) )
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
                

        else:
            
            d.append(loc)
    d1 = []
    d2 = []
    for num in range(0, len(d)): 
        if num % 2 == 0: 
            d1.append(d[num])

        else:
            d2.append(d[num])
    
    for l1 in merge(d1, d2):
        location_name  = " ".join(l1[0])
        street_address = l1[1][0].split(',')[0]
        
        city = l1[1][0].split(",")[1]
        state = l1[1][0].split(",")[-1].split()[0]
        zipp = l1[1][0].split(",")[-1].split()[-1]
        phone = l1[1][1].replace("Phone:","").strip()
        hours_of_operation ="   ".join(l1[1][2:]).replace("Hours:","").strip() 
        latitude    = "<MISSING>"
        longitude = "<MISSING>"
        store_number = "<MISSING>"
        try:
            location_type = location_name.split("Superstores")[1].replace("-","").replace("–","").strip()
        except:
            location_type = "<MISSING>"
        country_code = "US"
        store = [locator_domain, location_name,street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if str(store[2]) not in addresses:
            addresses.append(str(store[2]) )
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


    info1 = []
    for data1 in soup.find("div",{"class":"u_1877034994 dmNewParagraph"}):
        

        for br in data1.find_all("br"):
            br.replace_with("|")
        info1.append(data1.text)
    loc_list = " ; ".join(info1).split("|")
    d =[]
    for i in loc_list:
        loc = i.split("Food Shop")[0].split(" ; ")
        loc = [el.replace('\xa0','') for el in loc]
        loc = [x for x in loc if x != '']
        
        if loc == []:
            continue
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(loc[0]))
        if len(loc) >= 4 and us_zip_list == []:
            
            location_name = loc[0].strip()
            address = loc[1].split(",")
            if len(address) > 2:
                street_address = address[0]
                city = address[1]
                state = address[-1].split()[0]
                zipp = address[-1].split()[-1]
            else:
                street_address = address[0]
                city= address[-1].split()[0]
                state =address[-1].split()[1] 
                zipp =address[-1].split()[-1] 
            
            phone = loc[2].replace("Phone:","").strip()
            hours_of_operation = "  ".join(loc[3:]).replace("Hours:","").strip()
            latitude    = "<MISSING>"
            longitude = "<MISSING>"
            store_number = "<MISSING>"
            location_type = location_name.split("Superstores")[1].replace("-","").replace("–","").strip()
                
            country_code = "US"
            store = [locator_domain, location_name,street_address, city, state, zipp, country_code,store_number, phone, location_type if location_type else "<MISSING>", latitude, longitude, hours_of_operation, page_url]
            
            if str(store[2]) not in addresses:
                addresses.append(str(store[2]) )
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
                

        else:
            
            d.append(loc)
    d1 = []
    d2 = []
    for num in range(0, len(d)): 
        if num % 2 == 0: 
            d1.append(d[num])

        else:
            d2.append(d[num])
    
    for l1 in merge(d1, d2):
        location_name  = " ".join(l1[0])
        street_address = l1[1][0].split(',')[0]
        
        city = l1[1][0].split(",")[1]
        state = l1[1][0].split(",")[-1].split()[0]
        zipp = l1[1][0].split(",")[-1].split()[-1]
        phone = l1[1][1].replace("Phone:","").strip()
        hours_of_operation ="   ".join(l1[1][2:]).replace("Hours:","").strip() 
        latitude    = "<MISSING>"
        longitude = "<MISSING>"
        store_number = "<MISSING>"
        try:
            location_type = location_name.split("Superstores")[1].replace("-","").replace("–","").strip()
        except:
            location_type = "<MISSING>"
        country_code = "US"
        store = [locator_domain, location_name,street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if str(store[2]) not in addresses:
            addresses.append(str(store[2]) )
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


