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
    base_url= "http://foodsource.net/index.php/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k = (soup.find_all("div",{"class":"locations-table"}))

    for i in k:
        p = i.find_all("span",{"class":"location-address"})

        for p1 in p:
            hours = ''
            phone =''
            tem_var=[]
            street_address =list(p1.stripped_strings)[0]
            city =list(p1.stripped_strings)[1].split(',')[0]
            state = list(p1.stripped_strings)[1].split(',')[1].split( )[0]
            zip1 = list(p1.stripped_strings)[1].split(',')[1].split( )[1]
            phone1  = list(p1.stripped_strings)[-1]
            
  
            if "Map & Directions" in phone1:
                phone = (list(p1.stripped_strings)[-3])
                hours = (list(p1.stripped_strings)[3:-3][0])
            else:
                phone = (phone1)
                hours = (" ".join(list(p1.stripped_strings)[3:-1]).replace("Raley’s Pharmacy Hours",""))
            
            store_name.append(street_address)
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zip1.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("foodsource")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)
        
    for i in range(len(store_name)):
        store = list()
        store.append("http://foodsource.net")
        store.append(store_name[i])
        store.extend(store_detail[i])

        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
