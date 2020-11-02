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
    base_url= "https://www.davescosmicsubs.com/wp-admin/admin-ajax.php?action=store_search&lat=41.4298516&lng=-81.39109989999997&max_results=25&search_radius=10&autoload=1"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    # data = soup.find_all("div",{"class":"address_block"})
    k = json.loads(soup.text)
    
    for i in k:
        tem_var=[]
        name = i['city']
        st = i['address']
        city = i['city']
        state = i['state']
        zip1 = i['zip']
        phone =i['phone']
        lat = i['lat']
        log = i['lng']
        
        if i['hours']:
            hours = (i['hours'].replace("\n"," "))
        else:
            hours =("<MISSING>")

        if zip1:
            zip2 = zip1
        else:
            zip2 = "<MISSING>"
        
        tem_var.append("https://www.davescosmicsubs.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state.replace("44256","<MISSING>"))
        tem_var.append(zip2)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("davescosmicsubs")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        return_main_object.append(tem_var)

  
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


