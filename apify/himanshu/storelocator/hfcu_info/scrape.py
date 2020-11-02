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
    base_url= "https://www.hfcu.info/about-us/locations-and-hours"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= (soup.find_all("div",{"class":"loc_list"}))
    
   

    for i in k:
        p =i.find_all("div",{"class":'listbox'})
        for j in p:
            tem_var=[]
            v=list(j.stripped_strings)[6:]

            if v[0]=="Fax:":
                del v[0]
                del v[0]

            if v[0]=='Hours':
                del v[0]

            if v[-1]=="Available after hours by appointment.":
                del v[-1]

            if v[-1]=="Coin counter available in lobby.":
                del v[-1]

            if v[-1]=="Walk-up ATM available.":
                del v[-1]
            hours = (" ".join(v).replace("Coin counter available in lobby",""))
            name = list(j.stripped_strings)[1]
            st = list(j.stripped_strings)[2]
            city = list(j.stripped_strings)[3].split(',')[0]
            state = list(j.stripped_strings)[3].split(',')[1].split( )[0]
            zip1 = list(j.stripped_strings)[3].split(',')[1].split( )[1]
            phone = list(j.stripped_strings)[5].replace('MYCU','').strip().replace('(','').replace(')','').strip()
            

            tem_var.append("https://www.hfcu.info")
            tem_var.append(name.replace("\x96",""))
            tem_var.append(st.replace("\x96",""))
            tem_var.append(city.replace("\x96",""))
            tem_var.append(state.replace("\x96",""))
            tem_var.append(zip1.replace("\x96",""))
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone.replace("\x96",""))
            tem_var.append("hfcu")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours.replace("\x96",""))
            return_main_object.append(tem_var)
            
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

