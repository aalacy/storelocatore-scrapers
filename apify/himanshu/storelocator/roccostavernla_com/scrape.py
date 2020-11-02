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
    base_url= "http://roccostavern.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
  
    name_store=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    k=(soup.find_all("div",{"class":"small-12 large-3 columns"}))

    for i in k:
        tem_var=[]
        name = list(i.stripped_strings)[0]
        st =list(i.stripped_strings)[2]
        city = list(i.stripped_strings)[3].split(',')[0]
        state = list(i.stripped_strings)[3].split(',')[1].split( )[0]
        if len(list(i.stripped_strings)[3].split(',')[1].split( ))==2:
            zipcode = (list(i.stripped_strings)[3].split(',')[1].split( )[1])
        else:
            zipcode = "<MISSING>"
        
        phone =list(i.stripped_strings)[4]
        hours = (" ".join(list(i.stripped_strings)[6:8]))

        tem_var.append("http://roccostavern.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("roccostavern")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
