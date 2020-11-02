import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jwtumbles_com')







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
    base_url= "https://tumbles.net/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    loc= soup.find_all("li",{"class":"dropdown"})
    for i in loc:
        for data in i.find_all("li"):
            page_url = data.find("a")['href']
            loc1 = session.get(data.find("a")['href'])
            soup= BeautifulSoup(loc1.text,"lxml")
            hours = " ".join(list(soup.find("div",{"class":'col-md-4 opening-hours'}).stripped_strings)).replace("\xa0","")
            name = list(soup.find("address").stripped_strings)[0]

            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), list(soup.find("address").stripped_strings)[1])
            state = list(soup.find("address").stripped_strings)[1].split(',')[-2]
            city = list(soup.find("address").stripped_strings)[1].split(',')[-3]
            st = " ".join(list(soup.find("address").stripped_strings)[1].split(',')[:-3])
            phone = list(soup.find("address").stripped_strings)[-2]
            # logger.info( list(soup.find("address").stripped_strings)[-2])

    
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            tem_var =[]
            tem_var.append("https://jwtumbles.com")
            tem_var.append(name)
            tem_var.append(st)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipp)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours)
            tem_var.append(page_url)
            # logger.info(tem_var)
            return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


