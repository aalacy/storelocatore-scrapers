import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lostpizza_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
    data = soup.find_all("div",{"class":"col-md-4"})
    for index,i in enumerate(data,start=0):
        page_url = i.find("a")['href']
        r1 = session.get(page_url)
        # logger.info(page_url)
        soup1= BeautifulSoup(r1.text,"lxml")
        log = soup1.find("iframe")["src"].split("2d")[1].split("!3d")[0]
        lat = soup1.find("iframe")["src"].split("2d")[1].split("!3d")[1].split("!2m")[0]
        full_address = list(i.stripped_strings)
        # logger.info(len(full_address))
        # logger.info(full_address[2])
        tem_var =[]
        if len(full_address)== 4:
            store_name.append(list(i.h1.stripped_strings)[0])
            street_address = list(i.stripped_strings)[1]
            phone =  list(i.stripped_strings)[2]
            # logger.info(phone)
            city="<MISSING>"
            state = "<MISSING>"
            zipcode="<MISSING>"
            hours="7 Days a Week: 11AM - 9PM"
        if len(full_address)== 5:
            store_name.append(list(i.h1.stripped_strings)[0])
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
        if len(full_address)== 7:
            store_name.append(list(i.h1.stripped_strings)[0])
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
        if len(full_address)== 6:
            store_name.append(list(i.h1.stripped_strings)[0])
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
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(log)
        tem_var.append(hours)
        tem_var.append(page_url)
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


