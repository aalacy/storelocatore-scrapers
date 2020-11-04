import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('thenaturalcafe_com')

session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    base_url = 'https://thenaturalcafe.com/'
    locator_domain = "https://thenaturalcafe.com/"
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
    page_url = 'https://thenaturalcafe.com/locations/'
 
    import warnings
    from requests.packages.urllib3.exceptions import InsecureRequestWarning



    warnings.simplefilter('ignore',InsecureRequestWarning)
    r = session.get('https://thenaturalcafe.com/locations/',headers = headers,verify = False)
    soup = BeautifulSoup(r.text,'lxml')
    # logger.info(soup.prettify())
    for loc in soup.find_all('div',class_='location'):
        iframe = loc.find('iframe')['src'].split('&ll=')
        if len(iframe) >1:
            latitude = iframe[-1].split('&')[0].split(',')[0]
            longitude = iframe[-1].split('&')[0].split(',')[1]
        else:
            longitude = loc.find('iframe')['src'].split('!2d')[-1].split('!3d')[0]
            latitude =  loc.find('iframe')['src'].split('!2d')[-1].split('!3d')[1].split('!')[0]
        list_address = list(loc.find('div').stripped_strings)
        location_name = list_address[0].strip()
        if len(list_address) >7:
            street_address = list_address[1].strip() +  " "+list_address[2].strip()
            city = list_address[3].split(',')[0].strip()
            state =  " ".join(list_address[3].split(',')[-1].split()[:-1]).strip()
            zipp = "".join(list_address[3].split(',')[-1].split()[-1]).strip()
            phone = " ".join(list_address).split('ph')[-1].split('Hours')[0].strip()
            hours_of_operation = " ".join(" ".join(list_address).split('ph')[-1].split('Hours')[1:]).strip()



        else:
            street_address = list_address[1].strip()
            city = list_address[2].split(',')[0].strip()

            if len(list_address[2].split(',')[1].split()) >1:
                state = list_address[2].split(',')[1].split()[0].strip()
                zipp =  list_address[2].split(',')[1].split()[-1].strip()
            else:
                state = "".join(list_address[2].split(',')[1])
                zipp= "<MISSING>"
            phone = list_address[4].strip()
            hours_of_operation = " ".join(" ".join(list_address).split('Hours')[1:]).strip()

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = [x if x else "<MISSING>" for x in store]

        if store[2] in addresses:
            continue
        addresses.append(store[2])

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)




    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
