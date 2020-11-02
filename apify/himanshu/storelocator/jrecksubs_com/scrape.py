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
    base_url1="http://jrecksubs.com/Location.html"
    r = session.get(base_url1)
    soup= BeautifulSoup(r.text,"lxml")

    return_main_object =[]
    store_detail =[]
    store_name=[]
    street_address =[]
    city =[]
    state =[]
    zipcode =[]
    phone =[]
    k = soup.findAll("td")
    for i in k:
        
        st = i.findAll("span",{"class":"style32"})
        if st !=[]:
            for j in st:
                if ",SYRACUSE AREA ," in j.text.replace("\r","").replace("\xa0","").replace("\n",",").split('  '):
                    pass
                else:
                    data = j.text.replace("\xa0","").replace("\n\n","").split('\n')
                    for d in data:
                        if  "SYRACUSE AREA" in d or "WATERTOWN AREA" in d or "NORTHERN NEW YORK AREA" in d:
                            pass
                        else:
                            if len(d.replace("ÂÂÂ"," ").replace("ÂÂ"," ").split(',')) != 1:
                                street_address.append(d.replace("ÂÂÂ"," ").replace("ÂÂ"," ").split(',')[0].split(' - ')[0])
                                city.append( d.replace("ÂÂÂ"," ").replace("ÂÂ"," ").split(',')[0].split(' - ')[1])
                                newst = d.replace("ÂÂÂ"," ").replace("ÂÂ"," ").split(',')
                                if "7843 Oxbow Road - Canastota" in newst or "369 South 2nd Street - Fulton" in newst or "525 Mill Street - Watertown" in newst or "7596 State Street - Lowville" in newst :
                                    del newst[0]
                                    street_address.append(newst[0].replace(" NY  13032  315-697-8218 636","").replace("NY  13069  315-598-1144 3179","").replace("NY  13601  315-782-6230Â210","").replace(" NY 13367 315-376-2285Â29","").strip().split(' - ')[0])
                                    city.append(newst[0].replace(" NY  13032  315-697-8218 636","").replace("NY  13069  315-598-1144 3179","").replace("NY  13601  315-782-6230Â210","").replace(" NY 13367 315-376-2285Â29","").strip().split(' - ')[1])
                                    state.append(newst[1].split( )[0])
                                    zipcode.append(newst[1].split( )[1])
                                    phone.append(newst[1].split( )[2])
                             
                                zipcode1  = d.replace("ÂÂÂ"," ").replace("ÂÂ"," ").split(',')[1]
                                if "636 South Main Street - Central Square" in zipcode1 or "3179 Erie Blvd. East - Dewitt" in zipcode1:
                                    state.append(zipcode1.strip().split(' ')[0])
                                    zipcode.append( zipcode1.strip().split(' ')[2])
                                    phone.append(zipcode1.strip().split(' ')[4])
                                else:
                                    state.append(zipcode1.split('Â')[0].split( )[0])
                                    zipcode.append(zipcode1.split('Â')[0].split( )[1])
                                    phone.append(zipcode1.split('Â')[0].split( )[2])
    
    for i in range(len(street_address)):
        store = list()
        store.append("http://jrecksubs.com")
        store.append(street_address[i])
        store.append(street_address[i])
        store.append(city[i])
        store.append(state[i])
        store.append(zipcode[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i].replace('Â',""))
        store.append("jrecksubs")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

