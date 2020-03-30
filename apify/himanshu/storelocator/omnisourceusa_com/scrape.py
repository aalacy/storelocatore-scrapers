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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://www.omnisourceusa.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    lat =[]
    log = []
    k= (soup.find_all("div",{"class":"contact-card-small"}))
    name1 = (soup.find_all("div",{"class":"contact-card-name mb-2"}))
    script = soup.find_all("script")
    for i in script:
        if "var omniLocations" in i.text:
            jn =i.text.replace("var omniLocations = [","").replace("];","").replace("'", '"').strip().replace("'","").replace("\'", "\"").replace('\t','').replace('\n','').replace(',}','}').replace(',]',']')
            # print(json.loads(jn,strict=False))
            for o in range(len(jn.split("lng"))):
                if o>0:
                    log.append(jn.split("lng")[o].split(' "lat":')[0].replace('": "','').replace('",',""))
                    lat.append(jn.split("lng")[o].split(' "lat":')[1].replace('": "','').replace('",',"").split("}")[0].replace('"',""))
           
    # exit()
    for index,i in enumerate(k):
        tem_var =[]
        name = name1[index].text.strip().lstrip()
        phone = list(i.stripped_strings)[-3]
        city = list(i.stripped_strings)[-5].split(',')[0]
        state = list(i.stripped_strings)[-5].split(',')[1].split( )[0]
        zip1 = list(i.stripped_strings)[-5].split(',')[1].split( )[1]
        st = (" ".join(list(i.stripped_strings)[:-5]))
        

        tem_var.append("https://www.omnisourceusa.com")
        tem_var.append(name)
        tem_var.append(st)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat[index])
        tem_var.append(log[index])
        tem_var.append("<MISSING>")
        tem_var.append("https://www.omnisourceusa.com/locations")
        # print(tem_var)
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


