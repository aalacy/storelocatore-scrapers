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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://apolloburgers.com/locations/"
    r = session.get(base_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    
    data = soup.find_all("div",{"class":"hentry","data-sync":"textbox_content"})
    

    store_name=[]
    store_detail=[]
    return_main_object=[]
   
    for i in data:
        h =i.find_all("h6")
                
        for h1 in h:
            store_name.append(h1.text)
        
        k =i.find_all("p")
        for j in k:
            tem_var =[]
            k1= (list(j.stripped_strings))
            if k1 !=[] and len(k1) !=1:
                street_address = list(j.stripped_strings)[0]
                if "copyright" in street_address.lower():
                    continue
                # print(street_address)
                city = list(j.stripped_strings)[1].replace("No. ","").split(",")[0]
                state = list(j.stripped_strings)[1].replace("No. ","").split(",")[1].split( )[0]
                zipcode = list(j.stripped_strings)[1].replace("No. ","").split(",")[1].split( )[1]

                if len(list(j.stripped_strings)) != 2:
                    phone  = list(j.stripped_strings)[2]
                    hours = (" ".join(list(j.stripped_strings)[3:]).replace("Downtown Ordering DoorDash Delivery",""))
                else:
                    phone = "<MISSING>"
                    hours = "<MISSING>"

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("apolloburgers")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours)
                store_detail.append(tem_var)
                    
   
  
    # print(store_detail)
    for i in range(len(store_name)):
        store = list()
        store.append("https://apolloburgers.com")
        store.append(base_url)
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


