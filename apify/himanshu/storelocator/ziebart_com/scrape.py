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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    addresses = []
    
    locator_domain = "https://www.ziebart.com"
       

    data = {"Longitude": "-71.1987762451",
    "Latitude": "46.8758392334",
    "callBack": "init_map",
    "telEnMobile": "1"}    
    r_json = session.post("https://www.uniglassplus.com/inc/ajax/rechSuccursale.cfm", data=data).json()
    for data in r_json['ARRSUCCURSALE']:
        location_name = data['SUCCURSALENOM']
        street_address = data['ADRESSE']
        city = data['VILLE']
        state = data['PROVINCE']
        zipp = data['CP']
        country_code = "CA"
        store_number = data['SUCCURSALEID']
        phone = data['TEL']
        location_type = data['SUCCURSALETYPE']
        latitude = data['POSLATITUDE']
        longitude = data['POSLONGITUDE']
        page_url = data['LIENDETAIL']
        
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            hours_of_operation = " ".join(list(soup1.find("div",{"id":"horaireSucc"}).stripped_strings))
        except:
            hours_of_operation = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses:
            addresses.append(str(store[1]) + str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
