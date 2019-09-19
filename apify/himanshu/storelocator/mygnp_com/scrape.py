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
    try:
        base_url= "https://www.mygnp.com/pharmacies/"
        r = requests.get(base_url)
        soup= BeautifulSoup(r.text,"lxml")
        store_name=[]
        store_detail=[]
        return_main_object=[]
        address=[]
        k= soup.find_all("ul",{"class":"states-list body-wrapper content-block"})
        k1 = soup.find_all("ul",{"class":"states-list body-wrapper content-block"})

        for i in k1:
            for j in (i.find_all('a')):
                r = requests.get(j['href'])
                soup1= BeautifulSoup(r.text,"lxml")
                a = (soup1.find_all("div",{"class":"location-card"}))
                for j in a:
                    tem_var=[]
                    r = requests.get(j.a['href'])
                    soup2= BeautifulSoup(r.text,"lxml")
                    j2 = json.loads(soup2.find("script",{"type":"application/ld+json"}).text)
                    # print(j2['geo'])
                    # exit()
                    # tem_var.append("https://www.mygnp.com")
                    store_name.append(j2['name'])
                    tem_var.append(j2['address']['streetAddress'])
                    tem_var.append(j2['address']['addressLocality'])
                    tem_var.append(j2['address']['addressRegion'])
                    tem_var.append(j2['address']['postalCode'])
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(j2['telephone'])
                    tem_var.append("mygnp")
                    tem_var.append(j2['geo']['latitude'])
                    tem_var.append(j2['geo']['longitude'])
                    if "openingHours" in j2:
                        tem_var.append( j2['openingHours'])
                    else:
                        tem_var.append("<MISSING>")
                    store_detail.append(tem_var)
                    # return_main_object.append(tem_var)
        # print(store_detail)
        for i in range(len(store_name)):
            store = list()
            store.append("https://www.mygnp.com")
            store.append(store_name[i])
            store.extend(store_detail[i])
            if store[3] in address:
                continue
            address.append(store[3])
            return_main_object.append(store)
    except:
       pass

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


