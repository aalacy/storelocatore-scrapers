import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('loscompadreslbc_com')





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
    base_url= "http://loscompadreslbc.com/services/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    marker  = soup.find_all("div",{"id":"pl-158","class":"panel-layout"})
    for i in marker:
        p = (i.find_all("div",{"class":"panel-grid-cell"}))
        for p1 in p:
            tem_var=[]
            
            v = list(p1.stripped_strings)
            if len(v) != 1 and  v!=[]:
                r1 = session.get(p1.find_all('a')[0]['href'])
                soup1= BeautifulSoup(r1.text,"lxml")
                hours = (" ".join(list(soup1.find("tbody",{"class":"lemon--tbody__373c0__2T6Pl"}).stripped_strings)))
                lat = (p1.find_all('a')[1]['href'].split('/@')[-1].split(',')[0])
                lon = p1.find_all('a')[1]['href'].split('/@')[-1].split(',')[1]
                tem_var.append("https://www.loscompadreslbc.com")
                tem_var.append(v[0].replace("\u2028",""))
                tem_var.append(v[1].replace("\u2028",""))
                tem_var.append(v[2].split(',')[0])
                tem_var.append(v[2].split(',')[1].split( )[0])
                tem_var.append(v[2].split(',')[1].split( )[1])
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(v[-1])
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lon)
                tem_var.append(hours)
                tem_var.append(p1.find_all('a')[0]['href'])
                # logger.info(tem_var)
                return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


