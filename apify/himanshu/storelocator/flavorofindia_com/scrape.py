import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.flavorofindia.com/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []
    hours =[]

    k=(soup.find_all("ul",{"class":"elementor-icon-list-items"}))

    for i in k:
        city =''
        street_address=''
        tem_var =[]
        store_name.append(list(i.stripped_strings)[0])
        zip1 = list(i.stripped_strings)[1].split( )[-1]
        state = list(i.stripped_strings)[1].split( )[-2]
        phone  = list(i.stripped_strings)[2]
        hours = (" ".join(list(i.stripped_strings)[4:]))
        if "Burbank," in list(i.stripped_strings)[1].split( ):
            city = list(i.stripped_strings)[1].split( )[-3]
            street_address = (" ".join(list(i.stripped_strings)[1].split( )[:-3]))
        
        else:
            city =" ".join(list(i.stripped_strings)[1].split( )[-4:][:-2])
            street_address = (" ".join(list(i.stripped_strings)[1].split( )[:-4]).replace("#105,",""))

 

        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zip1.strip())
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("flavorofindia")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        store_detail.append(tem_var)


    for i in range(len(store_name)):
        store = list()
        store.append("https://www.flavorofindia.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
