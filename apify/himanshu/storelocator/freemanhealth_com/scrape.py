import csv
from bs4 import BeautifulSoup
import re
import json
import requests


def write_output(data):
    with open('data.csv', mode='w',newline='', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    addressesess=[]
    headers = {
    'accept': "application/json, text/javascript, */*; q=0.01",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    }
    result_coords = []
    link={33:"https://www.freemanhealth.com/locations/location-search-results?PostalCode=85029&LocationDescendants=true&page=1&count=5",18:"https://www.freemanhealth.com/locations/location-search-results?PostalCode=85029&LocationDescendants=true&page=1&count=10",8:"https://www.freemanhealth.com/locations/location-search-results?PostalCode=85029&LocationDescendants=true&page=1&count=25",5:"https://www.freemanhealth.com/locations/location-search-results?PostalCode=85029&LocationDescendants=true&page=1&count=50"}
    
    for q in link:
        for i in range(0,q):
            url123 = str(link[q].split("page=")[0].replace("1",'')+"page="+str(i)+"&"+link[q].split("page=")[1].split("&")[1])
            response = requests.get(url123, headers=headers)
            soup=BeautifulSoup(response.text,'lxml')
            data = soup.find(lambda tag: (tag.name == "script") and "var g_ihApplicationPath" in tag.text.strip())
            data1=json.loads(data.text.split("moduleInstanceData_IH_Public")[-1].split(" = ")[1].split(" if (!window.controllerNames)")[0].replace("};","}"))
            page_url1=[]
            for d in json.loads(data1['SettingsData'])['Records']:
                for d1 in d['StaticPageZones']:
                    for d2 in d1['Value']['FieldColumns']:
                        for d3 in d2['Fields']:
                            if "URL" in d3 and "location" in d3['URL']:
                                if str(d3['URL']) not in addresses :
                                    addresses.append(str(d3['URL']))
                                    if "/location/" in d3['URL']:
                                        page_url1.append("https://www.freemanhealth.com"+d3['URL'])
            # print(page_url1)
            for urls in page_url1:
                response1 = requests.get(urls, headers=headers)
                soup1 = BeautifulSoup(response1.text, "lxml")
                # latitude = str(soup1).split("center: {")[1].split("},")[0].split("lat: ")[1].split(",")[0]
                # longitude = str(soup1).split("center: {")[1].split("},")[0].split("lng: ")[1].split(",")[0]
                street_address=(soup1.find("meta",{"itemprop":"streetAddress"})['content'])
                name=soup1.find_all("meta",{"itemprop":'name'})[-1]['content']
                # print(name)
                city = soup1.find("meta",{"itemprop":"addressLocality"})['content']
                state = soup1.find("meta",{"itemprop":"addressRegion"})['content']
                zipp = soup1.find("meta",{"itemprop":"postalCode"})['content']
                phone = soup1.find("meta",{"itemprop":"telephone"})['content']    
                loctype = "<MISSING>"
                store_number = "<MISSING>"
                store = []
                store.append("https://www.freemanhealth.com")
                store.append(name) 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append(store_number if store_number else "<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(urls)
                if store[2] in addressesess:
                    continue
                addressesess.append(store[2])
                # print("data ==="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store
                        
        
                  
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
