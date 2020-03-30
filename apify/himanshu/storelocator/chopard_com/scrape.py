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
    locator_domain = "https://www.chopard.com/"
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


    get_data_url = 'https://www.chopard.com/intl/storelocator'
    r = session.get(get_data_url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")
    json_data = json.loads(soup.find('select', {'class': 'country-field'}).find_previous('script').text.replace(
        'var preloadedStoreList =', '').replace(';', '').strip())
    for x in json_data['stores']:
        try:
            if x['country_id'] in ['US' ,'CA']:
                page_url = x['details_url']
                store_number =x['store_code']
                location_name = x['name'].capitalize()
                if x['address_2'] ==None and x['address_3'] == None:
                    street_address = x['address_1']
                elif x['address_2'] !=None and x['address_3'] == None:
                    street_address = x['address_1'] +" "+ x['address_2']
                elif x['address_1'] !=None and x['address_2'] !=None and x['address_3'] !=None :
                    street_address = x['address_1'] +" "+ x['address_2'] +" "+ x['address_3']
                city = x['city']
                zipp = x['zipcode']
                # print(zipp)
                latitude = x['lat']
                longitude = x['lng']
                if x['phone'] != None:
                    phone = x['phone'].replace('\u200e','')
                else:
                    phone = "<MISSING>"
                country_code = x['country_id']
                page_url = x['details_url']
                r_loc = session.get(page_url,headers = headers)
                soup_loc = BeautifulSoup(r_loc.text,'lxml')
                col = soup_loc.find('div',class_='columns').find('div',class_='info-column').find('div',class_='shop-details')
                hours = col.find('p',class_ = 'opening')
                if hours != None:
                    h = hours.nextSibling.nextSibling
                    h_list = list(h.stripped_strings)
                    hours_of_operation = " ".join(h_list)
                    # print(hours_of_operation)

                else:
                    # print(page_url)
                    hours_of_operation = "<MISSING>"

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == "" or x == None or x == "." else x for x in store]

               # print("data = " + str(store))
               # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
        except:
            continue




    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
