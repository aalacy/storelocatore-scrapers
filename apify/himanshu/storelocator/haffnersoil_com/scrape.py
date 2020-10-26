import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('haffnersoil_com')


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
    # base_url= "https://woodys.com/locations/"
    # r = requests.get(base_url,headers=headers)
    # soup= BeautifulSoup(r.text,"lxml")
    # store_name=[]
    store_detail=[]
    return_main_object=[]

    url = "https://storelocator.w3apps.co/get_stores2.aspx?shop=haffners&all=1"
    headers = {
        'Accept': '*/*',
        'Content-Length': '0',
        'Origin': 'https://storelocator.w3apps.co',
        'Referer': 'https://storelocator.w3apps.co/map.aspx?shop=haffners&container=false',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = session.post(url, headers=headers).json()
    
    for data in response['location']:
        street_address = data['address']
        city =  data['city']
        state =  data['state']
        zip1 =  data['zip']
        phone =  data['phone']
        lat =  data['lat']
        lon =  data['long']
        name =  data['name']
        store_number = data['id']
        base_url='https://haffnersoil.com/'
        location_type = data['marker']
        tem_var=[]
        tem_var.append(base_url)
        tem_var.append(name)
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state.strip())
        tem_var.append(zip1.strip())
        tem_var.append("US")
        tem_var.append(store_number)
        tem_var.append(phone)
        tem_var.append(location_type)
        tem_var.append(lat)
        tem_var.append(lon)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        # logger.info(tem_var)
        yield tem_var



def scrape():
    data = fetch_data()
    write_output(data)


scrape()


