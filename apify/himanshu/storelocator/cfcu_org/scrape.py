import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cfcu_org')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://www.cfcu.org/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k= (soup.find_all("div",{"class":"loc_list"}))

    kk = soup.find('div',{'class':'pinned'}).find_next('script').text.split('var point = new google.maps.LatLng')
    main = []  
    for key,val in enumerate(kk):
            if key != 0:
                bb = val.split(';')[0].replace(')','').replace('(','').strip(',')
                if bb in main:
                    continue                
                main.append(val.split(';')[0].replace(')','').replace('(','').strip(','))
                
    
    for i in k:
        p =i.find_all("div",{"class":'listbox'})
        i = 0
        for j in p:
            tem_var=[]
            name = list(j.stripped_strings)[0]
            st = list(j.stripped_strings)[1]
            city = list(j.stripped_strings)[2].split(',')[0]
            state = list(j.stripped_strings)[2].split(',')[1].split( )[0]
            zip1 = list(j.stripped_strings)[2].split(',')[1].split( )[1]
            phone = list(j.stripped_strings)[4]
            v= list(j.stripped_strings)[5:]

            if v[0]=="Fax:":
                del v[0]
                del v[0]

            if v[0] =="Mailing Address:":
                del v[0]
                del v[0]

            if v[0] == "Mailing Address/ Loan Payments:":
                del v[0]
                del v[0]
            if v[0] =="Coin Counter":
                del v[0]
            hours = " ".join(v)
            latitude = main[i].split(',')[0]
            longitute = main[i].split(',')[1]

            

            tem_var.append("https://www.cfcu.org")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitute)
            tem_var.append(hours)
            tem_var.append(base_url)
            # logger.info(tem_var)
                    
            yield tem_var    
            i+=1

    


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


