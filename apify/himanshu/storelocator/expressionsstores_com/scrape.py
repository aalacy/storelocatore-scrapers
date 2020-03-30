import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    return_main_object = []
   


    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data
    base_url = 'https://www.expressionsstores.com/'
    locator_domain = "https://www.expressionsstores.com/"
    page_url = "<MISSING>"
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

    r = session.get('https://www.expressionsstores.com/locations-contact',headers = headers)
    soup= BeautifulSoup(r.text,'lxml')
    # print(soup.prettify())

    for info in soup.findAll('div',class_='txtNew')[2:]:
        list_info = list(info.stripped_strings)
        split_text =  " ".join(list_info).split('--------------------------------------------------------------------')

        for i in split_text:
            loc_list= i.split(',')
            street_address = " ".join(loc_list[0].replace('R.I.','').replace('M.A.','').replace('C.T.','').strip().split()[:-1]).replace(' E.','').replace('Jamaica','').replace('New','').replace('Fall','').replace('W.','').replace('Hyde','')
            city_tag= "".join(loc_list[0].replace('R.I.','').replace('M.A.','').replace('C.T.','').strip().split()[-1])
            # print(city_tag)
            if "Plains" == city_tag or "Bedford" == city_tag or "River" == city_tag or "Haven" == city_tag:
                city = " ".join(loc_list[0].replace('R.I.','').replace('M.A.','').replace('C.T.','').strip().split()[-2:])
            else:
                city = city_tag
            state_zipp =loc_list[1].split('P')[0].split()
            if len(state_zipp) >1:
                state = state_zipp[0].strip()
                zipp = state_zipp[-1].strip()
            else:
                state = state_zipp[0]
                zipp = "<MISSING>"
            phone = loc_list[1].split('P')[-1].split()[-1]
            location_name = city

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == None else x for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)
    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
