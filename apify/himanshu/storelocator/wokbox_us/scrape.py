import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://wokbox.us/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    tem_var=[]
    
    k = soup.find("table")
    info = list(k.stripped_strings)
    street_address = info[7].replace("TX,","").replace("USA","")
    city = info[6]
    store_name.append(info[6])
    state = info[7].split(',')[1].split( )[2]
    phone = info[10].replace("Phone: ","")
    time = info[8] + ' ' + info[9]

    tem_var.append(street_address)
    tem_var.append(city)
    tem_var.append(state)
    tem_var.append("<MISSING>")
    tem_var.append("US")
    tem_var.append("<MISSING>")
    tem_var.append(phone)
    tem_var.append("wokbox")
    tem_var.append("32.310491")
    tem_var.append("-95.299903")
    tem_var.append(time)
    store_detail.append(tem_var)
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://wokbox.us")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


