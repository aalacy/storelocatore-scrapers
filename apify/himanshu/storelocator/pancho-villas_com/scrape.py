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
    base_url= "http://pancho-villas.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k = (soup.find_all("div",{"id":"content"}))

    for i in k:
        p = i.find_all("p")
        for j in p:
            latitude =''
            longitude=''
            tem_var=[]
            if len(j.a['href'].split("&ll="))==2:
                latitude = j.a['href'].split("&ll=")[1].split("&")[0].split(',')[0]
                longitude  = j.a['href'].split("&ll=")[1].split("&")[0].split(',')[1]
            else:
                latitude = (j.a['href'].split('@')[1].split(",17z")[0].split(',')[0])
                longitude = (j.a['href'].split('@')[1].split(",17z")[0].split(',')[1])


            phone=list(j.stripped_strings)[-1]
            city = list(j.stripped_strings)[-2].split(',')[0]
            state = list(j.stripped_strings)[-2].split(',')[1].split( )[0]
            zipcode =list(j.stripped_strings)[-2].split(',')[1].split( )[1] 
            st = list(j.stripped_strings)[-3]
            name = " ".join(list(j.stripped_strings)[:-3])

            tem_var.append("http://pancho-villas.com")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("pancho-villas")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append("<MISSING>")
            return_main_object.append(tem_var)
    return return_main_object
   



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
