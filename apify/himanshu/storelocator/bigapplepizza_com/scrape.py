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
    base_url= "https://www.bigapplepizza.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    data = soup.find_all("div",{"class":"sprocket-mosaic-text"})
    name = soup.find_all("h2",{"class":"sprocket-mosaic-title"})

    for n in name:
        store_name.append(list(n.stripped_strings))
    for i in data:
        
        v=list(i.stripped_strings)
        del v[-1]
        
        
        if "33408" in v:
            tem_var =[]
            street_address = v[0]
            city = v[1].split(',')[0]
            state = v[1].split(',')[1].strip()
            zipcode = v[2]
            hours = (" ".join(v[4:]))
            phone = "<MISSING>"

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.replace('.',""))
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("bigapplepizza")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours)
            store_detail.append(tem_var) 
            
        
        else:
            tem_var =[]
            street_address = (",".join(v[:2]).split("FL")[0].strip().split(',')[0])
            city = (",".join(v[:2]).split("FL")[0].strip().split(',')[1])
            state = (" ".join(v[1:2]).split( )[-2])
            zipcode = (" ".join(v[1:2]).split( )[-1])
            phone = v[-4].replace("Phone: ","")
            hours = " ".join(v[4:6])
            
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.replace('.',""))
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("bigapplepizza")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours)
            store_detail.append(tem_var) 
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.bigapplepizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
