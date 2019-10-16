import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time


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
    locator_domain = "https://bernardcallebaut.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= requests.get('https://www.cococochocolatiers.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'html.parser')
    div = soup.find('div',class_='vc_tta-panels')
    for body in div.find_all('div',class_='vc_tta-panel'):
        heading = body.find('div',class_='vc_tta-panel-heading').text.strip()
        for d in body.find_all('div',class_='vc_col-sm-3'):
            list_d = list(d.stripped_strings)
            if list_d != []:
                # print(list_d)
                # print(len(list_d))
                # print('~~~~~~~~~~~~~~~~~~')


                if "UNITED STATES" == heading:
                    country_code = "US"

                else:
                    country_code = "CA"
                if len(list_d) ==10:
                    location_name = list_d[0]
                    city = list_d[0]
                    state= heading
                    street_address= list_d[1]
                    phone =list_d[3]
                    hours_of_operation = " ".join(list_d[6:8])
                    # print(location_name,city,state,street_address,phone,hours_of_operation,country_code)
                elif len(list_d) ==11:

                    location_name = " ".join(list_d[:2])
                    city = list_d[0]
                    state= heading
                    street_address = list_d[2]
                    phone = list_d[4]
                    hours_of_operation = " ".join(list_d[7:9])
                elif len(list_d) == 12:
                    location_name = list_d[0]
                    city = list_d[0]
                    state= heading
                    street_address = " ".join(list_d[1:3])
                    phone = list_d[4]
                    hours_of_operation = " ".join(list_d[7:9])
                elif len(list_d) ==13:
                    location_name = list_d[0]
                    city = list_d[0]
                    state = "<MISSING>"
                    cs =list_d[0].split('/')
                    # print(cs)
                    if len(cs) ==1:
                        city = "".join(cs).strip()
                        state = heading
                    else:
                        city = cs[0].strip()
                        state = cs[-1].split(',')[-1].strip()
                        # print(city,state)
                    street_address = " ".join(list_d[1:4]).replace('—','').replace('Store Hours','').replace('Phone','')
                    phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")," ".join(list_d))[0]
                    # print(phone)
                    hours_of_operation = " ".join(list_d).split('Store Hours')[-1].split('Holiday')[0].strip()
                    # print(location_name,city,state,street_address,phone,hours_of_operation,country_code)


                elif len(list_d) ==14:
                    location_name = " ".join(list_d[:2])
                    city = list_d[0]
                    state = heading
                    street_address = " ".join(list_d[2:4]).replace('—','')
                    phone= re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")," ".join(list_d))[0]
                    hours_of_operation = " ".join(list_d).split('Store Hours')[1].split('Holiday')[0]
                else:
                    location_name = " ".join(list_d[:2])
                    city = list_d[0]
                    state = heading
                    phone =  re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")," ".join(list_d))[0]
                    hours_of_operation = " ".join(list_d).split('Store Hours')[1].split('Holiday')[0]
                    if "CALGARY" != list_d[0]:
                        street_address = list_d[2]
                    else:
                        street_address = " ".join(list_d[2:7]).replace('Phone','').strip()

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == ""  else x for x in store]

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
