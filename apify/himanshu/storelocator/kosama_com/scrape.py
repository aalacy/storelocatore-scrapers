import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import json
# import sgzip
# import calendar
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kosama_com')







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
    # zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []



    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    #     "accept": "application/json, text/javascript, */*; q=0.01",
    #     # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # }

    # it will used in store data.
    locator_domain = "https://www.kosama.com/"
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

    url = "https://www.kosama.com/find"

    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"}

    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text,'lxml')
    content = soup.find('div',class_='content').find('div',{'id':'accordion'})
    for loc in content.find_all('ul',class_='state'):
        try:
            for li in loc.find_all('li'):
                page_url = "https://www.kosama.com"+li.find('a',class_ = 'panel')['href']
                location_name = li.find('div',class_='name').text.strip()
                address = li.find('div',class_='address')
                list_address= list(li.stripped_strings)
                if len(list_address) >4:
                    street_address = list_address[1] +" "+list_address[2]
                    city = list_address[3].split(',')[0].strip()
                    state = list_address[3].split(',')[-1].split()[0].strip()
                    zipp = list_address[3].split(',')[-1].split()[-1].strip()
                    phone = list_address[-1].strip()
                else:
                    street_address = list_address[1].strip()
                    city = list_address[2].split(',')[0].strip()
                    state = list_address[2].split(',')[-1].split()[0].strip()
                    zipp = list_address[2].split(',')[-1].split()[-1].strip()
                    phone = list_address[-1].strip()
                coords = session.get(page_url,headers = headers)
                soup_coords = BeautifulSoup(coords.text,'lxml')
                c1 = []
                c2 = []
                for iframe in soup_coords.find_all('iframe'):
                    if len(iframe['src'].split('&')) != 1:
                        c1.append(iframe['src'].split('&')[-5].split('=')[-1])
                        c2.append(iframe['src'].split('&')[-6].split('=')[-1])


                    else:
                        c1.append("<MISSING>")
                        c2.append("<MISSING>")
                if "Omaha North" != location_name:
                    latitude = c1.pop(-1)
                    longitude = c2.pop(-1)
                else:
                    latitude = c1.pop(-2)
                    longitude = c2.pop(-2)
                # logger.info(latitude,longitude,page_url)

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                store = ["<MISSING>" if x == "" or x == "Blank" else x for x in store]
                # if store_number in addresses:
                #     continue
                # addresses.append(store_number)

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
        except:
            continue

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
