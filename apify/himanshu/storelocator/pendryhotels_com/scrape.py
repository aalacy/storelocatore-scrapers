import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
   
    locator_domain = "https://pendryhotels.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get('https://www.pendry.com/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    info = soup.find('div',{'class':'menu-pendry'}).find('div',class_='col-md-4 order-md-5 menu-pendry__column-outer')
    for a in info.find_all('a'):
        # print(a['href'])
        r_loc = session.get(a['href'],headers = headers)
        soup_loc =BeautifulSoup(r_loc.text,'lxml')
        loc = soup_loc.find('span',class_= 'page-footer__address page-footer__address--small')
        list_loc = list(loc.stripped_strings)
        if list_loc != []:
            page_url = a['href'].strip()
            phone = list_loc[0].replace('Tel:','').strip()
            address = list_loc[-1].split(',')
            street_address = address[0].strip()
            city = address[1].strip()
            location_name =city
            # print(location_name)
            if len(address) >3:

                state = address[2].strip()
                zipp= address[-1].strip()
            else:

                state = address[-1].split()[0].strip()
                zipp = address[-1].split()[-1].strip()
            # print(city,zipp,state,street_address)
            latitude = loc.find('a')['href'].split('@')[-1].split(',')[0].strip()
            longitude = loc.find('a')['href'].split('@')[-1].split(',')[1].strip()

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == None  else x for x in store]

            #print("data = " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)





    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
