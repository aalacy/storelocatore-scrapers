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

    base_url1="https://www.seasonspizza.com/stores/elkton/"
    r = session.get(base_url1)
    main_soup= BeautifulSoup(r.text,"lxml")

    return_main_object =[]
    store_detail =[]
    store_name=[]
    info = main_soup.find_all("div",{"class":"row text-center"})
    
    for i in info:
        list1=[]
        link = i.find_all("a")
        for a in link:
            if "https://" in a['href']:
                pass
            else:
                list1.append(a['href'])
        if len(list1)==28:
            for j in range(len(list1)):
                tem_var=[]
                
                r = session.get("https://www.seasonspizza.com/"+list1[j])
                soup= BeautifulSoup(r.text,"lxml")
                title = soup.find("div",{"class":"panel-heading"})

                lat = (soup.find_all("script")[-1].text.split("new google.maps.LatLng")[1].split("var var_mapoption")[0].split(");")[0].replace("(","").split(",")[0])
                log  = (soup.find_all("script")[-1].text.split("new google.maps.LatLng")[1].split("var var_mapoption")[0].split(");")[0].replace("(","").split(",")[1])
               
               
                store_name.append(title.text.replace("\n","").replace("\r",""))

                hours = soup.find_all("dd")
                time =''
                for hour in hours:
                    time = time + ' ' +hour.text
                
                
                data= list(soup.find("address").stripped_strings)

                if len(data)==5:
                    street_address = data[2]
                    city = data[3].split(',')[0]
                    state =  data[3].split(',')[1].split( )[0]
                    zipcode =  data[3].split(',')[1].split( )[1]
                    phone =data[4]
                    hours_of_operation = time

                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("seasonspizza")
                    tem_var.append(lat)
                    tem_var.append(log)
                    tem_var.append(hours_of_operation)
                    store_detail.append(tem_var)

                else:
                   
                    street_address = data[1]
                    city = data[2].split(',')[0]
                    state =  data[2].split(',')[1].split( )[0]
                    zipcode =  data[2].split(',')[1].split( )[1]
                    phone =data[3]
                    hours_of_operation = time

                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("seasonspizza")
                    tem_var.append(lat)
                    tem_var.append(log)
                    tem_var.append(hours_of_operation)
                    store_detail.append(tem_var)
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.seasonspizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




