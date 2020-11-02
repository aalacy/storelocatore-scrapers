import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('myaroundtheclockfitness_com')







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
    base_url= "http://myaroundtheclockfitness.com/gyms/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    # k= (soup.find_all("div",{"class":"loc_list"}))
    # k = soup.find_all('a',{'class':'btn fcs-btn'})
    

    for data in soup.find_all("div",{"class":"col-sm-4"}):
        link = data.find("a",{"class":"btn fcs-btn"})
        if link != None:
            r1 = session.get(link['href'])
            soup1= BeautifulSoup(r1.text,"lxml")
            
            page_url1 = link['href']
            #logger.info(page_url1)
            # store_name = soup.find_all('div', {'class': 'fusion-title'}).text
            store_name = (soup1.find('div', {'class': 'fusion-title'}).text)
            phone =list(soup1.find_all('div', {'class':'fusion-text'})[1].stripped_strings)[-1]
            state = list(soup1.find_all('div', {'class':'fusion-text'})[1].stripped_strings)[-2].replace("FL,","FL").split(",")[-1].strip().split(" ")[0]
            zip1 = list(soup1.find_all('div', {'class':'fusion-text'})[1].stripped_strings)[-2].replace("FL,","FL").split(",")[-1].strip().split(" ")[-1]
            city =  list(soup1.find_all('div', {'class':'fusion-text'})[1].stripped_strings)[-2].split(",")[0]
            address = " ".join(list(soup1.find_all('div', {'class':'fusion-text'})[1].stripped_strings)[:-2])
            script = soup1.find(lambda tag: (tag.name == "script") and "addresses" in tag.text)
            latitude = json.loads(script.text.split("addresses: ")[1].split("animations:")[0].replace("}],","}]"))[0]['latitude']
            longitude = json.loads(script.text.split("addresses: ")[1].split("animations:")[0].replace("}],","}]"))[0]['longitude']
            tem_var =[]
            tem_var.append("http://myaroundtheclockfitness.com/")
            tem_var.append(store_name)
            tem_var.append(address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            # logger.info(tem_var)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append("<MISSING>")
            tem_var.append(page_url1)
           # logger.info(tem_var)
            yield tem_var
            # return_main_object.append(tem_var)
        

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
