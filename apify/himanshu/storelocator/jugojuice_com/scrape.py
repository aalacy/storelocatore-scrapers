import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jugojuice_com')





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
    
    r = session.get("https://www.jugojuice.com/en/locations/list", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
   
    
   
    
    k  = soup.find_all('article', {'class': 'location'})

    for i in k:
        lat = i.find('img')['src'].split('center=')[1].split('&zoom')[0].split(',')[0]
        lng = i.find('img')['src'].split('center=')[1].split('&zoom')[0].split(',')[1].strip()
        address_tmp =  list(i.stripped_strings)
        location_name = i.find('h3', {'itemprop': 'name'}).text.strip()
        address = i.find('span', {'itemprop': 'streetAddress'}).text.strip()
        city = i.find('span', {'itemprop': 'addressLocality'}).text.strip()
        state = i.find_all('span', {'itemprop': 'addressRegion'})[0].text.strip()
        zip = i.find_all('span', {'itemprop': 'addressRegion'})[1].text.strip()
        phone = i.find('span', {'itemprop': 'telephone'}).text.strip()
        country_code = i.find('span', {'itemprop': 'addressCountry'}).text.strip()    
        hour = i.find('div', {'class': 'hours'}).text.strip().replace('\n', '').replace('\r', '').replace('Hours','')  


    
      
       
        tem_var=[]       
        tem_var.append('https://www.jugojuice.com/')
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append(country_code)
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hour)
        tem_var.append("<MISSING>")
        #logger.info(tem_var)
        tem_var = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in tem_var]
        if 'Dubai' in city:
            continue
        yield tem_var

    # return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
