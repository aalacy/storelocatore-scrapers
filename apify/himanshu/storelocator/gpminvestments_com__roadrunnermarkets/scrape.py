import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gpminvestments_com__roadrunnermarkets')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    addresses = []
    r = session.get(
        "https://gpminvestments.com/store-locator/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find_all("script",{"type":"text/javascript"})
    for d in script:
        if "wpgmaps_localize_marker_data" in d.text:
            kd=d.text.split("var wpgmaps_localize_cat_ids =")[0].split("wpgmaps_localize_marker_data = ")[1].replace("};","}")
        
            # .split("var wpgmaps_localize_marker_data = ")[1].replace('"}}};',"}}}")
    
            for data in json.loads(kd):
                
                for key in json.loads(kd)[data].keys():
                    full_address=(json.loads(kd)[data][key]['address'])
                    if "," in full_address:
                        addr = full_address.split(",")
                        if len(addr) == 2:
                            # logger.info(full_address)
                            street_address = "233 Main St., PO Box 711"
                            city = "Preston"
                            raw_address = full_address
                            
                           
                        elif len(addr) == 4:
                            street_address = addr[0]
                            city = addr[1]
                            raw_address = "<MISSING>"
                    elif "\t" in full_address:
                        raw_address = "<MISSING>"
                        addr = full_address.split("\t")
                        if len(addr) == 2:
                        
                            street_address = " ".join(addr[0].split(" ")[:-1])
                            city = addr[0].split(" ")[-1]
                        else :
                            street_address = addr[0]
                            city = addr[1]
                    else:
                        raw_address = "<MISSING>"
                        addr = re.sub(r'\s+'," ",full_address).split(" ")
                        if len(addr[-1]) == 0:
                            del addr[-1]
                        if addr[-1].replace("-","").isdigit():
                            del addr[-1]
                        if addr[-1].replace("-","").isdigit():
                            del addr[-1]
                        if len(addr[-1]) == 2:
                            del addr[-1]
                        street_address = " ".join(addr[:-1])
                        city = addr[-1]

                    locatin_name = json.loads(kd)[data][key]['title']
                    latitude = json.loads(kd)[data][key]['lat']
                    longitude = json.loads(kd)[data][key]['lng']

                    state_list = re.findall(r'([A-Z]{2})', str(full_address.replace(", United States","").replace("US","")))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address).replace(", United States","").replace("US","").replace(", USA",''))


                    if state_list:
                        state = state_list[-1]

                    # logger.info(full_address)
                    if us_zip_list:
                        zipp = us_zip_list[-1]

                    else:
                        zipp = "<MISSING>"
                    # all_data =full_address.replace(state,'').replace(zipp,'').replace(", USA",'').replace(", United States",'').lstrip(",")

                    store = []
                    if "E-Z Mart" in street_address:
                        street_address = "15503 Babcock Rd"
                        city ="Antonio"
                        zipp="78255"
                        state = "TX"
                    if "1108 Western Avenue" in street_address:
                        latitude="<MISSING>"
                        longitude = "<MISSING>"
                    store.append("https://gpminvestments.com/roadrunnermarkets")
                    store.append(locatin_name)
                    store.append(street_address)
                    store.append(city)
                   
                    if "233 Main St., PO Box 711" in street_address:
                        zipp="21655-2215"
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append("<MISSING>")  # phone
                    store.append("<MISSING>")  # location_type
                    store.append(latitude)
                    store.append(longitude)
                    store.append("<MISSING>")  # hours_of_operation
                    # store.append(full_address)
                    store.append("<MISSING>")  # page_url
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    return_main_object.append(store)
                    store = [str(x).encode('ascii', 'ignore').decode(
                        'ascii').strip() if x else "<MISSING>" for x in store]
                    store = ["<MISSING>" if x == "" or x == "  " else x for x in store]

                    yield store
                    # logger.info("data == " + str(store))
                    # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                            # logger.info(all_data)
                        # logger.info(state)

    


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
