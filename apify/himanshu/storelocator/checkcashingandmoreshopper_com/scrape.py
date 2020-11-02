import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('checkcashingandmoreshopper_com')





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
        # "accept": "*/*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "http://checkcashingandmoreshopper.com/"
    locator_domain = "http://checkcashingandmoreshopper.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "checkcashingandmoreshopper"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    r =session.get('http://checkcashingandmoreshopper.com/locations.html',headers = headers)
    soup = BeautifulSoup(r.text,"lxml")
    for tr in soup.find('table').find_all('tr')[2:]:
        a = tr.find('a')
        if len(a['href'].split('=')) ==14:
            latitude  = a['href'].split('=')[5].split(',')[0]
            longitude = a['href'].split('=')[5].split(',')[-1].split('&')[0]
        elif len(a['href'].split('=')) ==9:
            latitude  = a['href'].split('=')[3].split(',')[0]
            longitude = a['href'].split('=')[3].split(',')[-1].split('&')[0]
            
        else:
            latitude  = a['href'].split('=')[6].split(',')[0]
            longitude = a['href'].split('=')[6].split(',')[-1].split('&')[0]
        state_list = a['href'].split('=')[-2].split('+')
        if len(state_list) ==1:
            s = a['href'].split('=')[-4].split('+')
            if len(s)  == 1 and len(s) !=4:
                state = "<MISSING>"
            elif len(s) == 4:
                state = a['href'].split('=')[-3].split('+')[-2]
            else:
                state = s[-2]

        else:
            state = state_list[-2]
        


        list_tr = list(tr.stripped_strings)
        if len(list_tr) == 4:
            street_address = list_tr[0].replace('\n\t\t\t\t\t\t\t\t\t',"").strip()
            city  = list_tr[1].strip()
            location_name =city
            zipp = list_tr[2].strip()
            phone = list_tr[-1].strip()
        else:
            street_address =" ".join(list_tr[:-3]).replace('\n\t\t\t\t\t\t\t\t\t',"")
            city = list_tr[-3].strip()
            zipp = list_tr[-2].strip()
            phone = list_tr[-1].strip()
            location_name = city

        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')



        # logger.info("data===="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        return_main_object.append(store)

    return return_main_object







def scrape():
    data = fetch_data()
    write_output(data)
scrape()
