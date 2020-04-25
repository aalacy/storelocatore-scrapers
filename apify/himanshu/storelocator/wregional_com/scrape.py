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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.wregional.com"
    r = session.get(base_url+"/main/physician-locator?atoz=1")
    soup=BeautifulSoup(r.text,'lxml')
    # print(base_url+"/main/physician-locator?atoz=1")
    # exit()
    addresses=[]
    return_main_object = []
    main=soup.find('main',{"id":'inside-page'}).find('div',{"class":"page-content"}).find_all('div',{"class":"info"})
    for dt in main:
        lat="<MISSING>"
        log="<MISSING>"

        loc=list(dt.stripped_strings)
        store=[]
        if len(loc)==15:
            # print("https://www.wregional.com"+dt.find("a")['href'])
            r1 = session.get("https://www.wregional.com"+dt.find("a")['href'])
            soup1=BeautifulSoup(r1.text,'lxml')
            try:
                lat = soup1.text.split("new google.maps.LatLng(")[1].split(");")[0].split(',')[0]
            except:
                lat="<MISSING>"

            try:
                log = soup1.text.split("new google.maps.LatLng(")[1].split(");")[0].split(',')[1]
            except:
                log="<MISSING>"
            store.append(base_url)
            store.append(loc[2])
            store.append(loc[4])
            store.append(loc[6])
            store.append(loc[8])
            store.append(loc[10])
            store.append("US")
            store.append("<MISSING>")
            store.append(loc[12].split(",")[0].replace("(479) 443-7771 800 632-4601","800 632-4601"))
            store.append(loc[14])
            store.append(lat)
            store.append(log)
            store.append("<MISSING>")
            store.append("https://www.wregional.com"+dt.find("a")['href'])
            # print(store)

        else:
            if "Office Name" in loc[1]:
                r2 = session.get("https://www.wregional.com"+dt.find("a")['href'])
                soup2=BeautifulSoup(r2.text,'lxml')
                try:
                    lat = soup2.text.split("new google.maps.LatLng(")[1].split(");")[0].split(',')[0]
                except:
                    lat="<MISSING>"

                try:
                    log = soup2.text.split("new google.maps.LatLng(")[1].split(");")[0].split(',')[1]
                except:
                    log="<MISSING>"
                store.append(base_url)
                store.append(loc[2])
                store.append(loc[4])
                store.append(loc[6])
                store.append(loc[8])
                store.append(loc[10])
                store.append("US")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(loc[12].split(",")[0].replace("(479) 443-7771 800 632-4601","800 632-4601"))
                store.append(lat)
                store.append(log)
                store.append("<MISSING>")
                store.append("https://www.wregional.com"+dt.find("a")['href'])
            else:
                r3 = session.get("https://www.wregional.com"+dt.find("a")['href'])
                soup3=BeautifulSoup(r3.text,'lxml')
                try:
                    lat = soup3.text.split("new google.maps.LatLng(")[1].split(");")[0].split(',')[0]
                except:
                    lat="<MISSING>"

                try:
                    log = soup3.text.split("new google.maps.LatLng(")[1].split(");")[0].split(',')[1]
                except:
                    log="<MISSING>"
                store.append(base_url)
                store.append("<MISSING>")
                store.append(loc[2])
                store.append(loc[4])
                store.append(loc[6])
                store.append(loc[8])
                store.append("US")
                store.append("<MISSING>")
                store.append(loc[10])
                store.append(loc[12].split(",")[0].replace("(479) 443-7771 800 632-4601","800 632-4601"))
                store.append(lat)
                store.append(log)
                store.append("<MISSING>")
                store.append("https://www.wregional.com"+dt.find("a")['href'])
        
        return_main_object.append(store)
    # return return_main_object
    for data in range(len(return_main_object)):
        # list1 = []
        if return_main_object[data][2] in addresses:
            continue
        addresses.append(return_main_object[data][2])
        yield  return_main_object[data]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
