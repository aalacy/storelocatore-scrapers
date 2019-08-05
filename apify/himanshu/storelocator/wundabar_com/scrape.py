import csv
import requests
from bs4 import BeautifulSoup
import re
import json
​
​
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
​
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
​
​
def fetch_data():
    base_url = "https://www.wundabar.com/studios"
    r = requests.get(base_url)
    main_soup= BeautifulSoup(r.text,"lxml")
    data1 = main_soup.find_all('div',{"class":"margin-wrapper"})
    return_main_object =[]
    store_detail =[]
    store_name=[]
    for i in data1:
        r = requests.get("https://www.wundabar.com"+i.a['href'])
        soup= BeautifulSoup(r.text,"lxml")
        
        k = soup.find_all("div",{"class":"sqs-block-content"})
        for i  in k:
            tem_var=[]
            if i != None:
                info = list(i.stripped_strings)
                if info != []:
                    state =''
                    zipcode =''
                    if "CONTACT" in info or len(info) ==1:
                        pass
                    else:
                        street_address = info[0]
                        city = info[1].split(',')[0]
                        store_name.append(city)
                        state_zip =  info[1].split(',')[1].split( )
                        if len(state_zip) ==3:
                            state = state_zip[0]+' '+state_zip[1]
                            zipcode = state_zip[2]
                        else:
                            state = state_zip[0]
                            zipcode = state_zip[1]
​
                        phone=info[2]
                        tem_var.append(street_address)
                        tem_var.append(city)
                        tem_var.append(state)
                        tem_var.append(zipcode)
                        tem_var.append("US")
                        tem_var.append("<MISSING>")
                        tem_var.append(phone)
                        tem_var.append("wundabar")
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        tem_var.append("<MISSING>")
                        store_detail.append(tem_var) 
​
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.wundabar.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
​
    print(len(return_main_object))
    return return_main_object
​
​
def scrape():
    data = fetch_data()
    write_output(data)
​
​
scrape()
