import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fatshack_com')





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
    base_url= "https://www.fatshack.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"html.parser")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    time =[]
    phone_no =[]
    k = soup.find_all("div",{"class":"location-box"})

    for i in k:
        names =  i.find_all("div",{"class":"location-name"})
        phones =  i.find_all("div",{"class":"location-box-contact-text"})
        hours =  i.find_all("div",{"class":"location-box-hours-wrapper"})

        for hours1 in hours:
            if "location-box-contact-text" in list(hours1.text):
                pass
            else:
                # time.append()
                time.append(" ".join(list(hours1.stripped_strings)[1:]).replace("Â","").replace("â","").replace("\xa0",""))
                # logger.info(time.encode('\x80','replace'))
        for phone in phones:
            if len(phone.text.split(',')) ==1:
                phone_no.append(phone.text.split(',')[0])
            tem_var =[]
            if len(phone.text.split(',')) !=1:
                if "3578 Hartsel Drive Colorado Springs" in phone.text.split(','):
                    city = " ".join( phone.text.split(',')[0].split( )[3:])
                    street_address= " ".join(phone.text.split( )[:3])
                    state = phone.text.split( )[-2]
                    zipcode = phone.text.split( )[-1]

                    tem_var.append(street_address)
                    tem_var.append(city.replace(",",""))
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    store_detail.append(tem_var)
  
              
                else:
                    if len(phone.text.split(',',2))==2:
                        street_address = " ".join(phone.text.split( )[:-3])
                        city=phone.text.split( )[:-2][-1]
                        state =  (phone.text.split( )[-2])
                        zipcode = (phone.text.split( )[-1])


                        tem_var.append(street_address)
                        tem_var.append(city.replace(",",""))
                        tem_var.append(state)
                        tem_var.append(zipcode)
                        store_detail.append(tem_var)
                    else:
                        street_address = phone.text.split(',',2)[0]
                        city = phone.text.split(',',2)[1]
                        state = phone.text.split(',',2)[2].split( )[0]
                        zipcode = phone.text.split(',',2)[2].split( )[1]

                        tem_var.append(street_address)
                        tem_var.append(city.replace(",",""))
                        tem_var.append(state)
                        tem_var.append(zipcode)
                        store_detail.append(tem_var)

        for name in names:
            store_name.append(name.text)
    del store_detail[10:]
    del store_name[10:]
    del phone_no[10:]
    del time[10:]
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.fatshack.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone_no[i])
        store.append("fatshack")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(time[i].replace("\x80","").replace("\x93",""))
        return_main_object.append(store)
  
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


