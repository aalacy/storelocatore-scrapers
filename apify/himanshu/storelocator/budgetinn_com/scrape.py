import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('budgetinn_com')




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
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "accept": "*/*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "http://budgetinn.com/"
    locator_domain = "http://budgetinn.com/"
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
    r= session.get("https://secure.rezserver.com/hotels/search/search_list.php?refid=5533&rooms=1&adults=2&children=0&express_deals=&query=11576&_=1570192273749",headers = headers)
    soup = BeautifulSoup(r.text,"lxml")
    # logger.info(soup.prettify())
    for ul in soup.find_all('ul'):
        for a in ul.find_all('a'):
            loc_id = a['href'].split('&')[-2]

            loc_type =  a['href'].split('&')[-2].split("_")[0]
            # logger.info(loc_type)
            r_loc = session.get('https://secure.rezserver.com/hotels/results_v2/list/?'+str(loc_id)+'&type='+str(loc_type)+'&rooms=1&adults=2&children=0&date_search=0&currency=USD&distance_unit=mile&search_type='+str(loc_type)+'&refid=5533',headers=headers)
            # logger.info('https://secure.rezserver.com/hotels/results_v2/list/?'+str(loc_id)+'&type='+str(loc_type)+'&rooms=1&adults=2&children=0&date_search=0&currency=USD&distance_unit=mile&search_type='+str(loc_type)+'&refid=5533')
            try:
                json_data = r_loc.json()
                # logger.info(json_data)
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            except Exception as e:
                logger.info("Error = "+ str(e))
                time.sleep(10)
                continue
            for z in json_data['hotels']:
                store_number =z['id']
                if store_number in addresses:
                        continue

                addresses.append(store_number)
                city_id = z['city_id']

                if city_id in loc_id:
                    location_type= "budgetinn"
                else:
                    location_type = "<MISSING>"
                # logger.info(location_type)


                location_name = z['name']
                address = z['address_display'].split(',')

                if len(address) ==6:
                    street_address = address[0].strip() + " "  + address[1].strip()
                    city = address[-2]
                    state = address[-1]
                elif len(address) ==5 or  len(address) == 4:
                    street_address =  " ".join(address[:-2]).strip().replace('New York','').replace('Jamaica','').replace('Ny','').strip()

                    city = address[-2].strip()
                    state = address[-1].strip()

                else :
                    street_address = address[0].strip()
                    city = address[-2].strip()
                    state = address[-1]
                    if " " == state:
                        state = "NY"





                latitude = z['geo']['latitude']
                longitude = z['geo']['longitude']
                page_url = "https://secure.rezserver.com"+z['href']




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
                if store[2] in addresses:
                        continue

                addresses.append(store[2])



                #logger.info("data===="+str(store))
                #logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

                return_main_object.append(store)

    return return_main_object







def scrape():
    data = fetch_data()
    write_output(data)
scrape()
