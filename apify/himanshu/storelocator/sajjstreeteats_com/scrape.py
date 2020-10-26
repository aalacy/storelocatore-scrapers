import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sajjstreeteats_com')




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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.sajjstreeteats.com/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []

   




    time = soup.find_all("div",{"class":"col-7 col-md-7 claro"})

    data = (soup.find("script",{"type":"application/ld+json"}))
    data1=json.loads(str(data).replace("</script>","").replace("<script type=","").replace('"application/ld+json">',""))

    for target_list in data1["subOrganization"]:
        tem_var=[]
    
        if "false" in target_list["hasMap"]:
            pass
        else:
            # logger.info()
            base_url= target_list["hasMap"]
            r = session.get(base_url,headers=headers)
            soup1= BeautifulSoup(r.text,"lxml").find("section",{"class":"content c-intro container-sm revealable"})
            hours=(" ".join(list(soup1.stripped_strings)[4:]))
        
        
        if target_list["telephone"] != None:
            phone  = (target_list["telephone"])
        if target_list["address"]["streetAddress"]:
            street_address = (target_list["address"]["streetAddress"])
            city = (target_list["address"]["addressLocality"])
            state = (target_list["address"]["addressRegion"])
            zipcode = (target_list["address"]["postalCode"])
            name = (target_list["address"]["name"])
            
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("sajjstreeteats")
            tem_var.append("<INACCESSIBLE>")
            tem_var.append("<INACCESSIBLE>")
            tem_var.append(hours)
            store_detail.append(tem_var)
         
            store_name.append(name)
        

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.sajjstreeteats.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


