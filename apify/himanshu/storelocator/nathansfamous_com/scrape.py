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
    return_main_object = []
    addresses = []

    base_url = "https://www.nathansfamous.com"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    output = []
    r = session.get("https://restaurants.nathansfamous.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    lat  =[]
    lng = []
    for lats in soup.find("div",{"id":"location-map"}).find_all("div",{"class":"et_pb_map_pin"}):
        lat.append(lats['data-lat'])
        lng.append(lats['data-lng'])
  
    for index,row in enumerate(soup.find_all("div",{"id":"twentyninepalms"})):
        full = list(row.stripped_strings)
        if full:
            if full[0]=="Dominican Republic":
                break
            else:
                phone = full[-1].replace(" x 115",'')           
                name = full[0]
                city=''
                zipp=''
                if len(full[2:-2])==3:
                    if full[2:-2][-1]=="32413":
                        del full[-1]
                    city = full[2:-2][-1].split(',')[0].replace("29 ",'')
                    state = full[2:-2][-1].split(",")[-1].split( )[0]
                    zipp = full[2:-2][-1].split(",")[-1].split( )[-1].replace("FL","32413")
                    if "801 Pier Park Drive" in full[2:-2][:-1] or "301 Mount Hope Avenue" in full[2:-2][:-1]:
                        address =" ".join(full[2:-2][:-1])
                    else:
                        name = full[2:-2][:-1][0]
                        address = " ".join(full[2:-2][:-1][1:])
                elif len(full[2:-2])==2:
                    state_list = re.findall(r' ([A-Z]{2})', str(full[2:-2][-1]))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full[2:-2][-1]))
                    if us_zip_list:
                        zipp = us_zip_list[-1]
                    else:
                        zipp=''
                    if state_list:
                        state = state_list[-1]
                    else:
                        state=""
                    city = full[2:-2][-1].replace(zipp,'').replace(state,'').replace(",",'')
                    address = " ".join(full[2:-2][:-1])
                    
                elif len(full[2:-2])==1:
                    state = full[2:-2][0].split(",")[-1].split( )[0]
                    zipp = full[2:-2][0].split(",")[-1].split( )[1]
                    city  = full[2:-2][0].split(",")[-2].replace("5770 W. Irlo Bronson Memorial Hwy ",'')
                    address = full[2:-2][0].split(",")[0].replace("Kissimmee",'')
                if "12475" in zipp :
                    state = "New York"
                    city = city.replace("Ruby New York","Ruby")
                if "10580" in zipp :
                    state = "New York"
                    city = city.replace("Rye New York","Rye")
                if "11364" in zipp :
                    state = "New York"
                    city = city.replace("Bayside New York","Bayside")
                if "10121" in zipp :
                    state = "New York"
                    city = city.replace("New York New York","New York")
                if "JFK Memorial Hwy. MM 82" in address:
                    state = "NY"
                    city = "New York"
                    address = address.replace('JFK Memorial Hwy. MM 82',"JFK Memorial Hwy. MM 82 Vesey St. & West St.")
                store = []
                store.append("http://nathansfamous.com/")
                store.append(name)
                store.append(address.strip())
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append(lat[index])
                store.append(lng[index])
                store.append("<MISSING>")
                store.append( "<MISSING>")     
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
