import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import sgzip
import json
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dilworthcoffee_com')




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
    # zips = sgzip.coords_for_radius(100)
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "https://www.dilworthcoffee.com/"
    locator_domain = "https://www.dilworthcoffee.com/"
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


    r = session.get('https://www.dilworthcoffee.com/wordpress1/wp-admin/admin-ajax.php?address=&formdata=addressInput%3D&lat=35.2270869&lng=-80.84312669999997&name=&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=base&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=Phone&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=Charlotte%2C+NC&options%5Bmap_center_lat%5D=35.2270869&options%5Bmap_center_lng%5D=-80.8431267&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Fwww.dilworthcoffee.com%2Fwordpress1%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fpin_chartreuse.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fwww.dilworthcoffee.com%2Fwordpress1%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_chartreuse.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bmessage_bad_address%5D=Could+not+locate+this+address.+Please+try+a+different+location.&options%5Bmessage_no_results%5D=No+locations+found.&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&radius=500&tags=&action=csl_ajax_onload',headers = headers).json()
    for loc_list in r['response']:
        try:
            country = loc_list['country'].strip()
            location_name = loc_list['name'].replace('&#039;',"'").strip()
            street_address = loc_list['address'] + " "+loc_list['address2'].strip()
            city = loc_list['city'].strip()
            state = loc_list['state'].strip()
            zipp= loc_list['zip'].strip()
            latitude = loc_list['lat'].strip()
            longitude = loc_list['lng'].strip()
            hours_of_operation = loc_list['hours'].replace('\r\n',' ').strip()
            page_url = loc_list['sl_pages_url'].strip()
            phone = loc_list['phone'].replace('Ext 333','').strip()
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
        except:
            continue

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)
scrape()
