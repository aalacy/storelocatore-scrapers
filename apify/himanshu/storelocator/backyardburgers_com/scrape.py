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
    base_url= "https://www.backyardburgers.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_detail=[]
    return_main_object=[]
    k = soup.find_all("a",{'class':"button -text-highlight"})
    lat1 =[]
    lng1=[]
    hours1=[]
    store_name=[]
    for i in k:
        tem_var=[]
        if "View Details" in i.text:
            r = session.get(i['href'])
            soup1 = BeautifulSoup(r.text,"lxml")
            v1 = list(soup1.find("article",{"class":"blog"}).stripped_strings)
            adr = soup1.find("div",{"class":"adr"})
            phone1 = soup1.find("div",{"class":"tel"})
            phone =(list(phone1.stripped_strings)[0])
            name = list(adr.stripped_strings)[0].split(",")[0]
            store_name.append(name)
            # print(name)
            st = list(adr.stripped_strings)[1]
            city = list(adr.stripped_strings)[2]
            zip1 = list(adr.stripped_strings)[5]
            state = list(adr.stripped_strings)[4]
            v1 = [p.replace("\xa0","") for p in v1]
            hours1.append(" ".join(v1[1:8]))
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("backyardburgers")
            print(tem_var)
            store_detail.append(tem_var)
        else:
            lat = i['href'].split("@")[-1].split(",")[0]
            lng = i['href'].split("@")[-1].split(",")[1]
            lat1.append(lat)
            lng1.append(lng)
            
        # tem_var.append("https://www.backyardburgers.com/")
        # store_name.append(name)
        # tem_var.append(st)
        # tem_var.append(city)
        # tem_var.append(state)
        # tem_var.append(zip1)
        # tem_var.append("US")
        # tem_var.append("<MISSING>")
        # tem_var.append(phone)
        # tem_var.append("backyardburgers")
       
        
        # print(tem_var)
        
    # print(store_name)
    # print(store_detail)
    for i in range(len(store_name)):
       store = list()
       store.append("https://www.backyardburgers.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       
       store.append(lat1[i])
       store.append(lng1[i])
       store.append(hours1[i])
       print(store)
       return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


