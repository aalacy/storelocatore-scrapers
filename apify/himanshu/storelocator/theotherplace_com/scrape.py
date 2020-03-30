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
    base_url= "https://theotherplace.com/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone1 =[]
    data = soup.find_all("div",{"class":"view-content"})




    for target_list in data:

        st = target_list.find_all("div",{"class":"field field--name-field-address field--type-string-long field--label-hidden field--item"})
        
        phone = target_list.find_all("div",{"class":"phone"})

        if phone !=[]:
            for p in phone:
                phone1.append(list(p.stripped_strings)[1])
  
        if st !=[]:
            for index,i in enumerate(st):
                tem_var =[]
                street_address = list(i.stripped_strings)[0]
                city = list(i.stripped_strings)[1].split(',')[0]
                state = list(i.stripped_strings)[1].split(',')[1].split( )[0]
                zipcod = list(i.stripped_strings)[1].split(',')[1].split( )[1]

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcod)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone1[index])
                tem_var.append("theotherplace")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("Monday-Friday 3-6pm")
                store_detail.append(tem_var)

        h4 =  target_list.find_all("h4")
        if h4 !=[]:
            for i in h4:
                store_name.append(list(i.stripped_strings)[0])

    for i in range(len(store_name)):
        store = list()
        store.append("https://theotherplace.com/")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
