import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cafemetrony_com')





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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "http://www.cafemetrony.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []
    hours =[]
    k = soup.find_all("div",{"class":"col-5 col-md-5 oscuro"})
    time = soup.find_all("div",{"class":"col-7 col-md-7 claro"})

    for t in time:
        hours.append( " ".join(list(t.stripped_strings)))
        
    
    for index,i in enumerate(k,start=0):
        tem_var =[]
        # logger.info(list(i.stripped_strings))
        st = list(i.stripped_strings)[0].replace("\n",',').split(',')[0]
        #
        city = list(i.stripped_strings)[1].split(',')[0]
        state = list(i.stripped_strings)[1].split(',')[1].strip().split(',')[0].split(' ')[0]

        zip1 = list(i.stripped_strings)[1].split(',')[1].strip().split(',')[0].split(' ')[1]
        phone = (list(i.stripped_strings))[-1]
        tem_var.append("https://cafemetrony.com")
        tem_var.append("<MISSING>")
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours[index])
        tem_var.append(base_url)

        yield  tem_var


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


