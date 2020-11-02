from bs4 import BeautifulSoup
import csv
import string
import re, time
from sgrequests import SgRequests
import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('petescorp_com')


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded'
}



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    data = []
    
    payload = {
    'action': 'csl_ajax_onload',
    'address': '',
    'formdata': 'addressInput%3D',
    'lat': '37.09024',
    'lng': '-95.712891',
    'options%5Bdistance_unit%5D': 'miles',
    'options%5Bdropdown_style%5D': 'none',
    'options%5Bignore_radius%5D': '0',
    'options%5Bimmediately_show_locations%5D': '1',
    'options%5Binitial_radius%5D': '',
    'options%5Blabel_directions%5D': 'Directions',
    'options%5Blabel_email%5D': '',
    'options%5Blabel_fax%5D': 'Fax',
    'options%5Blabel_phone%5D': 'Phone',
    'options%5Blabel_website%5D': 'Website',
    'options%5Bloading_indicator%5D': '',
    'options%5Bmap_center%5D': 'United+States',
    'options%5Bmap_center_lat%5D': '37.09024',
    'options%5Bmap_center_lng%5D': '-95.712891',
    'options%5Bmap_domain%5D': 'maps.google.com',
    'options%5Bmap_end_icon%5D': 'http%3A%2F%2Fpetescorp.com%2Fwp-content%2Fuploads%2F2019%2F06%2FPetes-Map-Logo.png',
    'options%5Bmap_home_icon%5D': 'https%3A%2F%2Fpetescorp.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_orange.png',
    'options%5Bmap_region%5D': 'us',
    'options%5Bmap_type%5D': 'roadmap',
    'options%5Bno_autozoom%5D': '0',
    'options%5Buse_sensor%5D': 'false',
    'options%5Bzoom_level%5D': '12',
    'options%5Bzoom_tweak%5D': '0',
    'radius': ''
    }
    p = 0
    session = SgRequests()
    r = session.post('https://petescorp.com/wp-admin/admin-ajax.php', headers=headers, data=payload)
    r.raise_for_status()
    data_dict = r.json()
    for location in data_dict['response']:
        lat = html.unescape(location['lat'])
        longt = html.unescape(location['lng'])
        title = html.unescape(location['name'])
        store = html.unescape(location['id'])
        hours = html.unescape(location['hours'])
        phone = html.unescape(location['phone'])
        street = html.unescape(location['address'])
        city = html.unescape(location['city'])
        state = html.unescape(location['state'])
        pcode = html.unescape(location['zip'])
        hours = hours.replace('am', ' am')
        hours = hours.replace('AM', ' AM')
        hours = hours.replace('PM', ' PM')
        hours = hours.replace('pm', ' pm')
        hours = hours.replace('-', ' - ')
        hours = hours.replace('OPEN ','')
        if len(store) < 1 or len(store)>5:
            store = "<MISSING>"
        if len(hours) < 2:
            hours = '<MISSING>'
        data.append([
                            'https://petescorp.com/',
                            'https://petescorp.com/home-page/store-locator/',                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            'US',
                            store,
                            phone,
                            "<MISSING>",
                            lat,
                            longt,
                            hours
                        ])
        #logger.info(p,data[p])
        p += 1
       
    
    
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
