import csv
import re
import pdb
import requests
from lxml import etree
import json
from bs4 import BeautifulSoup as bs

base_url = 'https://johnnysph.com'



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess=[]
    url =[]
    for q in range(0,22):
        base_url = "https://johnnysph.com/locations/3/?post%5B0%5D=jph_store&address%5B0%5D&units=imperial&per_page="+str(q)+"&lat&lng&form=2"
        soup = bs(requests.get(base_url).text,'lxml')
        script = soup.find(lambda tag: (tag.name == "script") and "var gmwMapObjects" in tag.text.strip()).text.split("var gmwMapObjects =")[1].split(";\n")[0]
        data = json.loads(script)
        for q in data:
            for tag in data[q]['locations']:
                soup1 = bs(tag['info_window_content'],'lxml')
                href = soup1.find("a")['href']
                name  = soup1.find("a").text
                if href not in url:
                    # 
                    url.append(href)
                    full = soup1.find("span",{"class":"address"}).text.split(",")
                    if "USA" in full[-1]:
                        del full[-1]
                    state = full[-1].strip().split( )[0]
                    zipp = full[-1].strip().split( )[1]
                    city = full[:-1][-1]
                    street_address = " ".join(full[:-2])
                    page_url = href
                    soup2 = bs(requests.get(href).text,'lxml')
                    phone='<MISSING>'
                    try:
                        soup3 = bs(requests.get(soup2.find("a",{"class":"btn-jph medium-grey btn-submit-order"})['href']).text,'lxml')
                        phone=(list(soup3.find("div",{"id":"viewOrderFrame"}).find("tr").stripped_strings)[-1])
                    except:
                        pass
                        # print(href)
                    # print(soup2)
                    lat = tag['lat']
                    lng =  tag['lng']
                    store = []
                    store.append("https://johnnysph.com/")
                    store.append(name.encode('ascii', 'ignore').decode('ascii').strip())
                    store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip())
                    store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
                    store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
                    store.append(zipp)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append( phone)
                    store.append("<MISSING>")
                    store.append(lat.strip() if lat.strip() else "<MISSING>" )
                    store.append(lng.strip() if lng.strip() else "<MISSING>")
                    store.append( "<MISSING>")
                    store.append(page_url)
                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    # store = [x.replace("–", "-") if type(x) ==
                    #          str else x for x in store]
                    store = [x.encode('ascii', 'ignore').decode(
                        'ascii').strip() if type(x) == str else x for x in store]
                    # print("data ===" + str(store))
                    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
