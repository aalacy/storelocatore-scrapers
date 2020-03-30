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
    base_url= "https://lostpizza.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    lat =[]
    lng =[]
    data = soup.find_all("div",{"class":"location-box"})
    # k =  soup.find_all("div",{"class":"col-md-4"})
    k =  soup.find("main",{"class":"site-main"}).find_all("div",{"class":"col-md-4"})
    
    for i in k:
        r2 = session.get(i.a['href'])
        soup1= BeautifulSoup(r2.text,"lxml")
        k1 = soup1.find_all("script",{"type":"text/javascript"})
        for i in k1:
            if  "var wpgmaps_localize_marker_data" in i.text:
                json1 = (i.text.split("var wpgmaps_localize_marker_data = ")[1].split("var wpgmaps_localize_cat_ids")[0].replace(";",""))
                for index,i in enumerate(json.loads(json1).keys()):
                    for j in json.loads(json1)[i].keys():
                        # print(json.loads(json1)[i][j]['address'])
                        lat.append(json.loads(json1)[i][j]['lat'])
                        lng.append(json.loads(json1)[i][j]['lng'])
    lat.insert(2,"<MISSING>")
    lng.insert(2,"<MISSING>")
    for index,i in enumerate(data,start=0):
        
        store_name.append(list(i.h1.stripped_strings)[0])
        tem_var =[]
        street_address = list(i.stripped_strings)[1]
        city = list(i.stripped_strings)[2].split(',')[0]
        state=list(i.stripped_strings)[2].split(',')[1].split( )[0]
        zipcode  = list(i.stripped_strings)[2].split(',')[1].split( )[1]
        phone =  list(i.stripped_strings)[3]
        v =list(i.stripped_strings)
        v.pop(0)
        v.pop(0)
        v.pop(0)
        v.pop(0)
        hours = "  ".join(v)
        # print("street_address====",street_address)
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("lostpizza")
        tem_var.append(lat[index])
        tem_var.append(lng[index])
        tem_var.append(hours)
        store_detail.append(tem_var)        

        
    for i in range(len(store_name)):
        store = list()
        store.append("https://lostpizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


