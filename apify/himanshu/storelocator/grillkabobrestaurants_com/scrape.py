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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "http://www.grillkabobrestaurants.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []
    k = soup.find_all("div",{"class":"hfeed"})

    for i in k:
        st = i.find_all("div",{"class":"one-half"})
        for std in st:
            p  = std.find_all("p")
            for p1 in p:
                tem_var =[]
                if  list(p1.stripped_strings) != []:
                    street_address = (list(p1.stripped_strings)[0])
                    city =  list(p1.stripped_strings)[1].split(',')[0]
                    state=list(p1.stripped_strings)[1].split(',')[1].split( )[0]
                    zipcode = list(p1.stripped_strings)[1].split(',')[1].split( )[1]
                    phone.append(list(p1.stripped_strings)[2])

                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    store_detail.append(tem_var)
                
    name = soup.find_all("h6")
    
    for i in range(len(name)):
        store = list()
        store.append("http://www.grillkabobrestaurants.com")
        store.append(name[i].text)
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("grillkabobrestaurants")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
