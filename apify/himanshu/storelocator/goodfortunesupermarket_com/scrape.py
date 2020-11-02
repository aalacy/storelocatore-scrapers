import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('goodfortunesupermarket_com')





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
    base_url= "http://goodfortunesupermarket.com/desktop.php?page=0&sale=ny"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
   
    k= soup.find_all("p",{"class":"address"})
    name1 = soup.find_all("div",{"class":"enlarge card"})
    
    phone1 = soup.find_all("div",{"class":"row icon_ctrl small-collapse"})
    for index,i in enumerate(k):
        tem_var =[]
        phone = (list(phone1[index].stripped_strings)[0].replace("\t","").replace("Phone: ","").replace("\n",""))
        # name = name1[index].text.strip().lstrip()
        name = (list(name1[index].stripped_strings)[0])
        if len(i.a['href'].split("@"))==2:
            lat = i.a['href'].split("@")[1].split(',')[0]
            log = i.a['href'].split("@")[1].split(',')[1]
        else:
            lat = "<MISSING>"
            log = "<MISSING>"
        zip1 = list(i.stripped_strings)[0].split(',')[-1].split( )[-1]
        state =list(i.stripped_strings)[0].split(',')[-1].split( )[-2]
        st  = list(i.stripped_strings)[0].split(',')[:-1][0].replace("Providence","")
        city = (list(i.stripped_strings)[0].split(',')[1].replace(" MA 02169","Quincy").replace("TX 75081","Richardson").replace(" RI 02907","Providence").replace("NY 11354","Flushing").strip())
       
        

        tem_var.append("http://goodfortunesupermarket.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(log)
        tem_var.append("<MISSING>")
        tem_var.append("http://goodfortunesupermarket.com/desktop.php?page=0&sale=ny")
        logger.info(tem_var)
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


