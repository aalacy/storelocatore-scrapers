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
    base_url= "http://www.malorestaurant.com"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = (soup.find("div",{"id":"text-2"}))
    k1 = (soup.find("div",{"id":"text-3"}))
    hors = " ".join(list(k.stripped_strings))
    v = list(k1.stripped_strings)
    # print(list(k1.stripped_strings))
    tem_var=[]
    tem_var.append("http://www.malorestaurant.com")
    tem_var.append(v[1].replace(", Silver Lake",""))
    tem_var.append(v[1].replace(", Silver Lake",""))
    # print(v[2])
    tem_var.append(v[1].split(",")[-2])
    # print(v[1].split(",")[-2])
    tem_var.append(v[2].split( )[0])
    tem_var.append(v[2].split( )[1])
    tem_var.append("US")
    tem_var.append("<MISSING>")
    tem_var.append(v[3].replace("Call: ",""))
    tem_var.append("malorestaurant")
    tem_var.append("<MISSING>")
    tem_var.append("<MISSING>")
    tem_var.append(hors.replace("Reservations & Hours ",""))
    # print(tem_var)
    return_main_object.append(tem_var)
    
    
       

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


