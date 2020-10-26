import csv
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import json
session = SgRequests()

def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    # search.current_zip()
    returnres=[]
    base_url="http://russellsconvenience.net"
    r = session.get("http://russellsconvenience.net/rcsver16/index.php/locations",headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    table =soup.find("div",{"class":"leading-0"}).find_all("tr",{"bgcolor":"#ccccff"})
    for index,tab in enumerate(table):
        if index>=9:
            add=list(tab.stripped_strings)
            zipp=''
            try:
                latitude = tab.find("a")['href'].split('/@')[1].split(',')[0]
                longitude =tab.find("a")['href'].split('/@')[1].split(',')[1]
                zipp =tab.find("a")['href'].split("+")[-1].split("/")[0]
                # print( )
            except:
                latitude="<MISSING>"
                longitude="<MISSING>"

            if len(add) > 1:
                city=''
                state=''
                
                if add[0][0].isdigit():
                    # print(add)
                    if "333 Market Street" in add:
                        name = "SAN FRANCISCO, CA"
                    if "199 Fremont Street" in add:
                        name = "SAN FRANCISCO, CA"
                    address = add[0]
                    city = add[1].split(',')[0]
                    state = add[1].split(',')[1].strip().split()[0]
                    zipp = add[1].split(',')[1].strip().split()[1]
                    phone = add[2]
                    hours = " ".join(add[3:])
                else:
                    name = add[0].replace("Russell's Fisher Pharmacy",'Fisher Building Russell s Fisher Pharmacy')
                    if "Fisher Building"==add[0]:
                        del add[0]
                    if "The Russ Building" in add:
                        name =  add[0]
                        address = add[1]
                        city = add[2].split(",")[0]
                        state = add[2].split(",")[1].strip().split()[0]
                        zipp =add[2].split(",")[1].strip().split()[1]
                        phone = add[3]
                        hours =" ".join(add[4:])
                    else:
                        name=add[0]
                        address = add[1]
                        # print(address)
                        if "505 S. Flower Street" in address or "333 S. Hope Street" in address:
                            city = "LOS ANGELES"
                            state = "CA"
                        if "2863 Kalakaua Avenue" in address:
                            city = "HONOLULU"
                            state = "HI"
                        if "3011 W. Grand Blvd." in address:
                            city = "DETROIT"
                            state = "MI"

                        phone = add[2]
                        hours = " ".join(add[3:])

                    
                store =[]
                store.append(base_url)
                store.append(name)
                store.append(address)
                store.append(city)
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours if hours else "<MISSING>")
                store.append("<MISSING>")
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
                yield store
    vk = soup.find("div",{"class":"leading-0"}).find("table",{"align":"center","style":"width: 100%; background-color: #f4f646;","border":"1","cellspacing":"2","cellpadding":"3"})
    name=vk.find("tr",{"bgcolor":"#ffffff"}).text.strip()
    for d in vk.find_all("tr",{"bgcolor":"#ccccff"}):
            for index,q in enumerate(str(d).split("#ffffff")):
                soups= BeautifulSoup(q,"lxml")
                add = list(soups.stripped_strings)
                zipp=''
                try:
                    latitude = soups.find("a")['href'].split("/@")[1].split(",")[0]
                    zipp = soups.find("a")['href'].split("+")[-1].split("/")[0]
                    longitude = soups.find("a")['href'].split("/@")[1].split(",")[1]
                except:
                    latitude="<MISSING>"
                    longitude="<MISSING>"
                if "Corporate Office" in add or "**NEW**" in add:
                    continue
                if "17th Street Building" in add:
                    name  ="DENVER, CO"
                    address = add[1]
                    # print(address)
                    phone = add[2]
                    hours =add[3]

                    store =[]
                    store.append(base_url)
                    store.append(name)
                    store.append(address)
                    store.append("DENVER")
                    store.append("CO")
                    store.append(zipp if zipp else "<MISSING>")
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(hours if hours else "<MISSING>")
                    store.append("<MISSING>")
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    yield store
                if "17th Street Building" in add:
                    name  =add[4]
                    address = add[5]
                    phone = add[6]
                    hours =add[7]
                if "17th Street Building" in add:
                    pass
                elif len(add) >1:
                    if '">' in add or '" width="2%">' in add:
                        del add[0]
                    if add[0][0].isdigit():
                        name = 'DENVER, CO'
                        address =add[0]
                        phone = add[2]
                        hours = " ".join(add[3:] )
                    else:
                        name =add[0]
                        address = add[1]
                        phone = add[2]
                        hours = " ".join(add[3:])
                        

                store =[]
                store.append(base_url)
                store.append(name)
                store.append(address)
                store.append("DENVER")
                store.append("CO")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                if "1225 17th Street" in address:
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                else:
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                store.append(hours if hours else "<MISSING>")
                store.append("<MISSING>")
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        
                yield store
        

def scrape():
    data = fetch_data();
    write_output(data)
scrape()
