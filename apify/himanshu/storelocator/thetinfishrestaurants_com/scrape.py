import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thetinfishrestaurants_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "x-requested-with":"XMLHttpRequest",
        "referer": "https://www.thetinfishrestaurants.com/locations-menus/find-a-tin-fish-location-near-you/",
        "content-type" :"application/x-www-form-urlencoded; charset=UTF-8",

    }
    data = 'address=&formdata=addressInput%3D&lat=37.09024&lng=-95.71289100000001&name=&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=10000&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=http%3A%2F%2Fwww.thetinfishrestaurants.com&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=United+States&options%5Bmap_center_lat%5D=37.09024&options%5Bmap_center_lng%5D=-95.712891&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=http%3A%2F%2Fwww.thetinfishrestaurants.com%2Fwp-content%2Fuploads%2F2013%2F01%2FTF-Marker.png&options%5Bmap_home_icon%5D=http%3A%2F%2Fwww.thetinfishrestaurants.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbox_yellow_home.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bmessage_bad_address%5D=Could+not+locate+this+address.+Please+try+a+different+location.&options%5Bmessage_no_results%5D=No+locations+found.&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=4&options%5Bzoom_tweak%5D=1&radius=10000&tags=&action=csl_ajax_onload'

    base_url= "https://www.thetinfishrestaurants.com/wp-admin/admin-ajax.php"
    loc = session.post(base_url,data=data,headers=headers).json()
    
    store_name=[]
    store_detail=[]
    time =[]
    return_main_object=[]
    phone = []
    
    for i in loc['response']:
        tem_var =[]
        address = i['address']
        city = i['city']
        lat= i['lat']
        lng =i['lng']
        name = i['name']
        phone = i['phone']
        state = i['state']
        zip1 = i['zip']
        hours = i['data']['sl_hours'].replace("\t","").strip().replace("\n","").replace("&#44;","")

        tem_var.append("https://www.thetinfishrestaurants.com")
        tem_var.append(name)
        tem_var.append(address.replace("\t","").replace("\n","").replace("\r",""))
        tem_var.append(city.replace("\t","").replace("\n","").replace("\r",""))
        tem_var.append(state.strip().replace("\t","").replace("\n","").replace("\r",""))
        tem_var.append(zip1.strip().replace("\t","").replace("\n","").replace("\r",""))
        tem_var.append("US")
        tem_var.append("<MISSING>")
        
        tem_var.append(phone.replace("\t","").replace("\n","").replace("\r",""))
        tem_var.append("<MISSING>")
        tem_var.append(lat.replace("\t","").replace("\n","").replace("\r",""))
        tem_var.append(lng.replace("\t","").replace("\n","").replace("\r",""))
        tem_var.append(hours.replace("\r","").replace(" &amp;",""))
        tem_var.append("<MISSING>")
        # logger.info(tem_var)
        return_main_object.append(tem_var)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


