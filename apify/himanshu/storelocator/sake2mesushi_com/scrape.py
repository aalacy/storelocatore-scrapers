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
    base_url= "http://sake2mesushi.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")

    return_main_object=[]

    tem_var=[]
    k=soup.find("div",{"class":"location margined"})
    latitude =k.a['href'].split("@")[1].split(",17z")[0].split(',')[0]
    longitude =k.a['href'].split("@")[1].split(",17z")[0].split(',')[1]
    name = list(k.stripped_strings)[0]
    phone=list(k.stripped_strings)[-2]
    st =list(k.stripped_strings)[1]
    city = list(k.stripped_strings)[2].split(',')[0]
    state = list(k.stripped_strings)[2].split(',')[1].split( )[0]
    zipcode = list(k.stripped_strings)[2].split(',')[1].split( )[1]
    
    k1=soup.find("div",{"id":"hours-cont"})
    hours = (" ".join(list(k1.stripped_strings)))

    tem_var.append("http://sake2mesushi.com")
    tem_var.append(name)
    tem_var.append(st)
    tem_var.append(city)
    tem_var.append(state)
    tem_var.append(zipcode)
    tem_var.append("US")
    tem_var.append("<MISSING>")
    tem_var.append(phone)
    tem_var.append("sake2mesushi")
    tem_var.append(latitude)
    tem_var.append(longitude)
    tem_var.append(hours)
    return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
