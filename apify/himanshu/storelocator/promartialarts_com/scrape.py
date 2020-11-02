import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','content-type':'application/x-www-form-urlencoded; charset=UTF-8'}
    return_main_object = []
    base_url = "https://promartialarts.com/"
    data = 'address=&formdata=addressInput%3D&lat=37.09024&lng=-95.71289100000001&name=&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=Phone&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=United+States&options%5Bmap_center_lat%5D=37.09024&options%5Bmap_center_lng%5D=-95.712891&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Fnewtempwebsite.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fpromartialarts.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fflag_azure.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bmessage_bad_address%5D=Could+not+locate+this+address.+Please+try+a+different+location.&options%5Bmessage_no_results%5D=No+locations+found.&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=0&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&radius=&tags=&action=csl_ajax_onload'
    r = session.post('https://promartialarts.com/wp-admin/admin-ajax.php',headers = header,data=data).json()
    
    for idx, val in enumerate(r['response']):
        locator_domain = base_url
        location_name = val['name'].strip().replace('&#039;s',' ')
        street_address = val['address'].strip()
        city = val['city'].strip()
        state = val['state'].strip()
        zip = val['zip'].strip()
        store_number = '<MISSING>'
        country_code = val['country'].strip()
        phone = val['phone'].strip().replace('(KICK)',"")
        location_type = 'promartialarts'
        latitude = val['lat'].strip()
        longitude = val['lng'].strip()
        hours_of_operation = val['hours'].strip()

        store=[]
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        
        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        return_main_object.append(store)
    return return_main_object
       
def scrape():
    data = fetch_data()  
    
    write_output(data)

scrape()
 



