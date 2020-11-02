import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('luxehotels_com')





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
    page_url = 'https://www.luxehotels.com/hotels"'
    r = session.get("https://www.luxehotels.com/hotels", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")




    k  = soup.find('div', {'class': 'address'}).find_all('li')[:-1]


    for i in k:
        tem_var = []
        location_name= i.find('p').find('span',{'class':'name'}).text
        phone= i.find('p').find('a',{'class':'phone-num'}).text
        add1 = i.find('p')
        address =  list(add1.stripped_strings)[1]
        city_tmp = list(add1.stripped_strings)[2].split(',')
        city = city_tmp[0]
        state_tmp = city_tmp[1].split(' ')
        state = state_tmp[1]
        zip = state_tmp[2]
        link= i.a['href']
        r1 = session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        lat =soup1.find_all('script', {'type': 'text/javascript'})
        # logger.info(lat)
        # logger.info(len(lat))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~')
        if(len(lat)==11):
            lat1= soup1.find_all('script', {'type': 'application/ld+json'})[2].text.split('"latitude": ')[1]
            latitude= lat1.split('longitude')[0].strip().replace('"','').replace(',','').strip()
            longitude= lat1.split('longitude')[1].split('"url":')[0].replace('": "','').strip().replace(' },','').replace('"','').strip()


        else:
            latitude = '<INACCESSIBLE>'
            longitude = '<INACCESSIBLE>'







        tem_var.append('https://www.luxehotels.com')
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zip)
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append("<MISSING>")
        tem_var.append(page_url)
       #logger.info(tem_var)
       #logger.info('~~~~~~~~~~~~~~~~~~~`')
        return_main_object.append(tem_var)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
