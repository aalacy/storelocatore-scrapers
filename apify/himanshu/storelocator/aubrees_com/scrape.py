import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('aubrees_com')





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
    location_name =[]
    r = session.get(
    "https://aubrees.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")


    location_name_tmp  = soup.find_all('h3', {'class': 'uk-accordion-title'})
    for i in location_name_tmp:
        location_name.append(i.text)
        # logger.info(location_name)
    address_tmp = soup.find_all('div', {'class': 'uk-margin'})
    for index,i in enumerate(address_tmp,start=0):
        tem_var = []
        address = list(i.stripped_strings)[0]
        # logger.info(address)
        city_tmp = list(i.stripped_strings)[1].split(',')
        city= city_tmp[0]
        state_tmp = city_tmp[1].split(' ')
        state = state_tmp[1]
        zip1= state_tmp[2]
        phone = list(i.stripped_strings)[2].replace('/ (734) 424-1402 (Delivery)','')
        hour = list(i.stripped_strings)[4:]
        hours_of_operation =  " ".join(hour).split('Aubree')[0]
        # logger.info(hours_of_operation)
        page_url = "<MISSING>"





        tem_var.append('https://aubrees.com/')
        tem_var.append(location_name[index])
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip1)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("aubrees")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours_of_operation)
        tem_var.append(page_url)
        logger.info("===="+str(tem_var))
        logger.info('~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(tem_var)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
