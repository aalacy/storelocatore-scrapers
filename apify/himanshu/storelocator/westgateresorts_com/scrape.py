# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json,urllib
import time
import lxml


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.westgateresorts.com/explore-destinations/"

    r = session.get(base_url)

    main_soup = BeautifulSoup(r.content,"lxml")
    return_main_object = []
    store_detail = []
    store_name = []
    k= main_soup.find_all("a",{'class':"button resort"})

    for i in k:
        tem_var =[]
        r = session.get("https://www.westgateresorts.com/"+i['href'])
        soup = BeautifulSoup(r.content,"lxml")

        info = soup.find('div',{'id':"footer-resort-info"})
        data = list(info.stripped_strings)
        name = data[0]
        store_name.append(name)
        street_address = data[1]
        city_zip = data[2]
        city = city_zip.split(',')[0]
        state = city_zip.split(',')[1].split( )[0]
        zipcode = city_zip.split(',')[1].split( )[1]
        phone  = data[3].split("Resort Phone:")[1]
        
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("westgateresorts")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.westgateresorts.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object
    



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
