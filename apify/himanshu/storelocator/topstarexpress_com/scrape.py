import csv
import requests
from bs4 import BeautifulSoup
import re
import json



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
    base_url = "https://www.topstarexpress.com/our-stores"

    r = requests.get(base_url)
    store_name = []
    soup = BeautifulSoup(r.content,"lxml")
    return_main_object =[]
    store_detail =[]
    k = soup.find_all('p',{"class":"","style":"white-space:pre-wrap;"})
    for i in k:
        data = list(i.stripped_strings)
        if len(data) !=1:
            temp_var = []
            store_name.append(data[0].split(" - NEW LOCATION!")[0].split(" - OPENING MAY 13TH WITH DRIVE THRU!")[0])
            street_address = data[0].split(" - NEW LOCATION!")[0].split(" - OPENING MAY 13TH WITH DRIVE THRU!")[0]
            city = data[1].split(',')[0]
            state = data[1].split(',')[1]
            phone  =  data[2]

            temp_var.append(street_address)
            temp_var.append(city)
            temp_var.append(state)
            temp_var.append("<MISSING>")
            temp_var.append("US")
            temp_var.append("<MISSING>")
            temp_var.append(phone)
            temp_var.append("topstarexpress")
            temp_var.append("<MISSING>")
            temp_var.append("<MISSING>")
            temp_var.append("<MISSING>")
            store_detail.append(temp_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.topstarexpress.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


