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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" ,"page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    
    address = []
    
    base_url= "https://lovinghut.us/locations/"
    r= session.get(base_url, headers=headers)
    soup=BeautifulSoup(r.text, "lxml")
    links=soup.find_all("td",{"class":"tg-citi"})
   
        
    for link in links:
        href = (link.a["href"])
        
        r1 = session.get(href, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        data = soup1.find("p",{"class":"section_text dark"})  
        if data != None:
            data1 = list(data.stripped_strings)
            iframe = soup1.find("iframe")
            if "1804 E Southern Ave #1" in data1:
                pass
            else:
                if iframe != None:
                    del data1[-1] 
                    phone = data1[-1]
                    del data1[-1]
                    city = data1[-1].split(',')[0]
                    state = data1[-1].split(',')[1].split(' ')[1]
                    zipp = data1[-1].split(',')[1].split(' ')[2].replace('1604','01604')
                    del data1[-1]
                    del data[-1]
                    street_address = " ".join(data1)
                    hours = soup1.find("table",{"class":"hours"})
                    h = list(hours.stripped_strings)
                    hours_of_operation=" ".join(h).encode('ascii', 'ignore').decode('ascii').replace('Kitchen is closed 20 minutes before closing time every lunch and dinner.','').replace('***','').replace('(buffet)','').replace('(menu)','').replace('(buffet + menu)','')
                    name = list(link.stripped_strings)
                    location_name = " ".join(name)
                    src = iframe.attrs["src"]
                    geo_request = session.get(src, headers=headers)
                    geo_soup = BeautifulSoup(geo_request.text, "lxml")

                    for script_geo in geo_soup.find_all("script"):
                        if "initEmbed" in script_geo.text:
                            geo_data = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                            latitude = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                            longitude = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
                                  
        
                    store = []
                    store.append("https://lovinghut.us")
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation)
                    store.append(href)
                    if store[2] in address:
                        continue
                    address.append(store[2])
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
