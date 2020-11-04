import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('firstunited_net')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    store_name = []
    return_main_object = []
    address1 = []
    
    r = session.get(
    "https://www.firstunited.bank/company/banking-center-atm-itm-locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    k  = soup.find_all('a', {'class': 'location-title'})
 

    for i in k:
        tem_var = []
        link = i['href']
        r1 = session.get(link, headers=headers)
        
        soup1 = BeautifulSoup(r1.text, "lxml")
        address_tmp = soup1.find('div', {'class': 'location-details'})
        location_name =  list(address_tmp.stripped_strings)[0]
        address = list(address_tmp.stripped_strings)[2]
        city_tmp = list(address_tmp.stripped_strings)[3].split(',')
        city = city_tmp[0]
        state_tmp = city_tmp[1].split(' ')
        state = state_tmp[1]
        zip1 =state_tmp[2]
        
       
        phone='<MISSING>'
        Address=''
        for index,i in enumerate(list(address_tmp.stripped_strings)):
            if "Phone Number:" in i:
                phone = list(address_tmp.stripped_strings)[index+1]
            
        for index,i in enumerate(list(address_tmp.stripped_strings)):
            if "P.O. Address:" in i:
                Address = list(address_tmp.stripped_strings)[index+1]

        if(len(list(address_tmp.stripped_strings))==15):
            hour = list(address_tmp.stripped_strings)[11]+''+list(address_tmp.stripped_strings)[12]+''+list(address_tmp.stripped_strings)[13]+''+list(address_tmp.stripped_strings)[14]
            
        elif(len(list(address_tmp.stripped_strings))==13):
            hour = list(address_tmp.stripped_strings)[11]+''+list(address_tmp.stripped_strings)[12]

        elif(len(list(address_tmp.stripped_strings))==17):
            hour = list(address_tmp.stripped_strings)[11]+''+list(address_tmp.stripped_strings)[12]+''+list(address_tmp.stripped_strings)[13]+''+list(address_tmp.stripped_strings)[14]+''+list(address_tmp.stripped_strings)[15]+''+list(address_tmp.stripped_strings)[16]
        loc=''    
        if "EARTH BANKING CENTER" in location_name or "LITTLEFIELD BANKING CENTER" in location_name or "SEAGRAVES BANKING CENTER" in location_name or "SUDAN BANKING CENTER" in location_name or "WICHITA FALLS BANKING CENTER" in location_name or "SEMINOLE BANKING CENTER" in location_name or "FIRST UNITED EXPRESS" in location_name or "DIMMITT BANKING CENTER" in location_name or "SOUTHEAST BANKING CENTER" in location_name:
            loc="Branch"
        else:
            loc="Branch & ATM"
        # logger.info(location_name)    
        tem_var.append('https://www.firstunited.net/')
        tem_var.append(location_name)
        tem_var.append(address+' '+Address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip1)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append(loc)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hour.replace("Motor Bank Hours:",' Motor Bank Hours: '))
        tem_var.append(link)
        tem_var = [str(x).strip() if x else "<MISSING>" for x in tem_var]
        yield tem_var

        # return_main_object.append(tem_var)
                   
 
    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
