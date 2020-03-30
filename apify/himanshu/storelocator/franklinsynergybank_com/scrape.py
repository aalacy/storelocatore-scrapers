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
    base_url= "https://www.franklinsynergybank.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
  
    k= soup.find_all("div",{"class":"wpb_column vc_column_container vc_col-sm-12"})

    for i in k:
        names = i.find_all("h2")
        p = i.find_all("div",{"class":"wpb_text_column wpb_content_element"})
        for p1 in p[:-6]:
            tem_var =[]
            if len(list(p1.stripped_strings)) !=1:
                store_name.append(list(p1.stripped_strings)[0])
                street_address =list(p1.stripped_strings)[1]
                city = list(p1.stripped_strings)[2].split(",")[0]
                state = list(p1.stripped_strings)[2].split(",")[1].split( )[0]
                zipcode =list(p1.stripped_strings)[2].split(",")[1].split( )[1]
                phone  = (list(p1.stripped_strings)[3])
                hours = (list(p1.stripped_strings)[5:][-1])

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("franklinsynergybank")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours)
                store_detail.append(tem_var)

   
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.franklinsynergybank.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
     
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


