import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('salo-salogrill_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
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
    domain_url = 'http://www.salo-salogrill.com/'
    get_url = "http://www.salo-salogrill.com/locations"
    r = session.get(get_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")    
    k  = soup.find_all('div', {'id': 'ctl01_divModMaps'})
    for i in k:

        address_tmp =list(i.stripped_strings)
        location_name = address_tmp[0]
        address  = address_tmp[1]
        city_tmp = address_tmp[2].split(',')
        city = city_tmp[0]
        state_tmp = city_tmp[1].strip().split(' ')
        state = state_tmp[0]
        zip = state_tmp[1]
        phone = address_tmp[3].strip().replace('Phone.','')
        if '91792' in zip:
            hour = soup.find('div',{'id':'ctl01_ctl00_description'}).text.replace('West Covina Hours','').strip().replace('\n','')
        else:
            hour = '<MISSING>'    
        tem_var = []                 
        tem_var.append(domain_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hour)
        tem_var.append(get_url)
        return_main_object.append(tem_var)
      
                   
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
