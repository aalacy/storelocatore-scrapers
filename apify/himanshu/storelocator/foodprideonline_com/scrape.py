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
    base_url = "https://foodprideonline.com/store-locations/"

    r = session.get(base_url)

    soup = BeautifulSoup(r.text,"lxml")

    count = 0

    return_main_object = []


    k=soup.find("div",{"class":"entry-content-wrapper clearfix"})

    store_names =[]

    store_detail = []

    # for tr  in k.find_all('h2'):
    #     store_names.append(tr.text)

    for tr in k.find_all('p'):

        temp_var = []

        temp = tr.text.split(',')
        street_address = temp[0].split("\n")[0]
        store_names.append(street_address)
        city = temp[0].split("\n")[1]
        state = temp[1].split( )[0]
        zipcode =  temp[1].split( )[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "Food Pride"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        
        temp_var.append(street_address)
        temp_var.append(city)
        temp_var.append(state)
        temp_var.append(zipcode)
        temp_var.append(country_code)
        temp_var.append(store_number)
        temp_var.append(phone)
        temp_var.append(location_type)
        temp_var.append(latitude)
        temp_var.append(longitude)
        temp_var.append(hours_of_operation)
        store_detail.append(temp_var)

    return_main_object = []

   
    for i in range(len(store_detail)):
        store= list()
        store.append("https://foodprideonline.com")
        store.append(store_names[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
        
    
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


