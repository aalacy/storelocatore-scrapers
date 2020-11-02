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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    base_url = "https://www.ronsburgersandchili.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    
    k= soup.find(class_="Index").find_all("div",{"class":"sqs-block-content"})
    for i in k:
        if "directions" not in str(i).lower():
            continue
        tem_var=[]
        latitude=''
        longitude=''
        names = i.find("h2")
    
        a = i.find("a",text="Directions")
        if a != None:
            if len(a['href'].split("@")) == 1:
                latitude="<MISSING>"
                longitude = "<MISSING>"
            else:
                latitude = a['href'].split("@")[1].split('z/')[0].split(',')[:-1][0]
                longitude =a['href'].split("@")[1].split('z/')[0].split(',')[:-1][1]

        if "Midwest City" in names.text:
            latitude="35.4678759"
            longitude = "-97.4782202"

        if "Jenks" in names.text:
            latitude="36.0230107"
            longitude = "-95.9769108"
            
        if names != None:
            name = list(names.stripped_strings)
            if "Site Map" in name or "Connect" in name or "Franchise" in name or "Subscribe" in name or "Contact" in name:
                pass
            else:
                store_name.append(name[0])

        info1 = i.find("p")
        if info1 != None:
            info = list(info1.stripped_strings)
            if "HOME" in info or "Interested in Franchising Opportunities? Contact us today." in info or  "Stay informed by signing up to our Newsletter." in info or "© 2016-2019 Ron's Hamburgers and Chili. All Rights Reserved." in info or "ADDRESS" in info:
                pass
            else:
                tem_var.append(info[0])
                tem_var.append(info[1].split(',')[0].replace("\xa0"," "))
                tem_var.append(info[1].split(',')[1].split( )[0].replace(" ",""))
                tem_var.append(info[1].split(',')[1].split( )[1])
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(info[2])
                tem_var.append("<MISSING>")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append("<MISSING>")
                store_detail.append(tem_var)
    
    for i in range(len(store_name)):
        store =list()
        store.append("ronsburgersandchili.com")
        store.append("https://www.ronsburgersandchili.com/locations")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    
    
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
