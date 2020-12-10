import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('catchairparty_com')





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
    locator_domain = "https://catchairparty.com"
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



    r= session.get('https://catchairparty.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    contain = soup.find('section',class_='location_top_main').find_all('div',class_ = 'row')[1]
    for tag in soup.find_all(lambda tag: tag.name == 'a' and 'title' in tag.attrs):

        a = tag['href'].split('//')[-1].split('/')
        if len(a) > 3:
            r_loc = session.get(tag['href'],headers = headers)
            s_loc = BeautifulSoup(r_loc.text,'lxml')

            info = s_loc.find('section',class_ = 'location_top_main').find_all('div',class_='row')[1]
            loc= info.find('div',class_ = 'col-xs-12')
            # logger.info(loc.prettify())
            page_url = tag['href']
            loc_list = list(loc.stripped_strings)
            location_name = loc_list[0].strip()
            address = loc_list[1].split(',')

            if len(address) ==3:
                street_address = address[0].strip()
                c = address[1].split()
                if len(c) ==1:
                    city = c[0].strip()
                else:
                    city = " ".join(c[2:])
                state = address[-1].split()[0].strip()
                zipp = address[-1].split()[-1].strip()

            elif len(address) ==2:
                zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
                if zipp_list != []:
                    zipp = zipp_list[0].strip()
                    state = address[-1].split()[0].strip()
                    city = " ".join(address[0].split()[-2:])
                    street_address = " ".join(address[0].split()[:-2])
                else:
                    street_address = " ".join(address).strip()
                    city = loc_list[2].split(',')[0].strip()
                    state= loc_list[2].split(',')[1].split()[0].strip()
                    zipp = loc_list[2].split(',')[1].split()[-1].strip()
            else:
                street_address = "".join(address)
                city = loc_list[2].split(',')[0].strip()
                state= loc_list[2].split(',')[1].split()[0].strip()
                zipp = loc_list[2].split(',')[1].split()[-1].strip()
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")," ".join(loc_list))[0]

            hours = info.find_all('div',class_ = 'col-xs-12')[1]
            list_hours = list(hours.stripped_strings)
            hours_of_operation = " ".join(list_hours[1:])


            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" or x == None  else x.strip() for x in store]
            # if street_address in addresses:
            #     continue
            # addresses.append(street_address)

            logger.info("data = " + str(store))
            logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
