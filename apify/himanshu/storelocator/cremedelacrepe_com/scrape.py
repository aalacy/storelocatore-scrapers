import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import calendar
# import json
# import sgzip
# import time



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




    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = 'http://www.cremedelacrepe.com/'
    locator_domain = "http://www.cremedelacrepe.com/"
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



    r= session.get('http://www.cremedelacrepe.com/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    loc = soup.find('li',class_='menu-item-303').find('ul',class_='sub-menu').find_all('a')
    for a in loc:
        r_loc = session.get(a['href'],headers = headers)
        s_loc = BeautifulSoup(r_loc.text,'lxml')

        detail = s_loc.find('div',class_='vc_col-sm-3')
        # print(detail.prettify())

        info = detail.find('div',class_='wpb_text_column')
        list_info = list(info.stripped_strings)
        p = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_info[-1]))
        phone = p[0]
        if len(list_info) ==3:
            street_address = list_info[0]
            city = list_info[1].split(',')[0]
            state = list_info[1].split(',')[1].split()[0]
            zipp = list_info[1].split(',')[1].split()[-1]


        else:
            street_address = " ".join(list_info[:2])
            city = list_info[2].split(',')[0]
            state = list_info[2].split(',')[1].split()[0]
            zipp = list_info[2].split(',')[1].split()[-1]
        location_name = city

        latitude = detail.script.text.split(':')[2].split('"')[1]
        longitude =detail.script.text.split(':')[3].split('"')[1]
        page_url = a['href']
        hour = s_loc.find('div',class_='vc_col-sm-9').find('div',class_='wpb_text_column wpb_content_element')
        
        if hour:
            list_hour = list(hour.stripped_strings)
            hours_of_operation = list_hour[0].split('Hour')[-1].replace('\xa0'," ").strip()
        else:
            hours_of_operation=''
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        for i in range(len(store)):
            if type(store[i]) == str:
                if store[i] != "<MISSING>":
                    store[i] = store[i].lower()
        print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
