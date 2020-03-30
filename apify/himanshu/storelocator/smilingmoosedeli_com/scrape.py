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
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/x-www-form-urlencoded"
    }
    data = 'address=11756&formdata=addressInput%3D11756&lat=40.7226698&lng=-73.51818330000003&name=&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D=1200&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Catering%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=Facebook&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=Denver%2C+CO&options%5Bmap_center_lat%5D=37.09024&options%5Bmap_center_lng%5D=-95.712891&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=http%3A%2F%2Fsmilingmoosedeli.com%2Fsmd-wp%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_red.png&options%5Bmap_home_icon%5D=http%3A%2F%2Fsmilingmoosedeli.com%2Fsmd-wp%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fflag_azure.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bmessage_bad_address%5D=Could+not+locate+this+address.+Please+try+a+different+location.&options%5Bmessage_no_results%5D=No+locations+found.&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=0&options%5Bzoom_level%5D=0&options%5Bzoom_tweak%5D=0&radius=50000&tags=&action=csl_ajax_search'
    r = session.post("http://smilingmoosedeli.com/smd-wp/wp-admin/admin-ajax.php",headers=headers,data=data)
    for store_data in r.json()["response"]:
        store = []
        store.append("http://smilingmoosedeli.com")
        store.append(store_data["name"])
        store.append(store_data["address"] + " " + store_data["address2"])
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["data"]["sl_id"])
        store.append(store_data["phone"].replace("DELI","") if store_data["phone"] else "<MISSING>")
        store.append("smiling moose deli moose")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append(store_data["hours"].replace("\r"," ").replace("\n"," ").replace("\t"," ") if store_data["hours"] else "<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()