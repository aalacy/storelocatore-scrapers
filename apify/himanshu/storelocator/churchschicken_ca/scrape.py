import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
from collections import Counter 
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('churchschicken_ca')




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
    address =[]
    return_main_object=[]
    address1 =[]
    base_url= "https://www.churchschicken.ca/"
    # base_url = 'https://www.churchschicken.ca/british-columbia/locations/'
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    links = soup.find("div",{"class":"fusion-alignright"}).find_all("a",{"class":"fusion-bar-highlight"})
    for link in links:
        page_url = link['href']
        if link['href'].count('/') != 6:
            continue
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")

        address_list = list(soup1.find_all("div",{"class":"fusion-text"})[0].find("p").stripped_strings)
        street_address = " ".join(address_list[:-2])
        if len(address_list[-1].split(" ")) == 2:
            city = address_list[-2].split(" ")[0]
            state = address_list[-2].split( )[-1]
            zipp = address_list[-1]
        else:
            city = address_list[-2]
            state = address_list[-1].split(" ")[0]
            zipp = " ".join(address_list[-1].split(' ')[1:])
        location_name = city
        country_code = "CA"
        store_number = "<MISSING>"
        phone = soup1.find_all("div",{"class":"fusion-text"})[1].find("p").text
        location_type = "Churchs Chicken"
        if soup1.find(lambda tag : (tag.name == "script") and "latitude" in tag.text):
            coords = soup1.find(lambda tag : (tag.name == "script") and "latitude" in tag.text).text
            latitude = coords.split('"latitude":"')[1].split('","')[0]
            longitude = coords.split('"longitude":"')[1].split('"')[0]
            
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        hours_of_operation = re.sub(r"\s+"," ",soup1.find_all("div",{"class":"fusion-text"})[2].find("p").text.strip())
    

        tem_var =[]
        tem_var.append("https://www.churchschicken.ca")
        tem_var.append(location_name )
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipp)
        tem_var.append("CA")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours_of_operation)
        tem_var.append(page_url)
        # logger.info("=============================================",tem_var)
        tem_var = [x.strip() if type(x) == str else x for x in tem_var]
        yield tem_var
     
  


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


