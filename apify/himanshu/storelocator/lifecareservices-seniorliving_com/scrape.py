import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# from sgrequests import SgRequests
# session = SgRequests()
import requests

def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    # locator_domain = "https://www.lifecareservices-seniorliving.com/"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    # location_url = "https://www.lifecareservices-seniorliving.com/"
    url = "https://www.lifecareservices-seniorliving.com/wp-admin/admin-ajax.php"

    data = {
            'pg': '1',
            'action': 'get_communities',
            'gd_nonce': '1a8e7200c4'
        }

    # payload = 'pg=%201&action=%20get_communities&gd_nonce=%201a8e7200c4'
    headers = {
    #   'Accept': '*/*',
    #   'Accept-Encoding': 'gzip, deflate, br',
    #   'Accept-Language': 'en-US,en;q=0.9',
    #   'Connection': 'keep-alive',
    #   'Content-Length': '47',
    #   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #   'Cookie': 'PHPSESSID=b4802e21f7b7fd12016652baa283117e; resolution=1600; _gcl_au=1.1.1322420874.1590408589; _ga=GA1.2.1900899838.1590408590; _gid=GA1.2.1086599991.1590408590; __insp_wid=117628331; __insp_nv=true; __insp_targlpu=aHR0cHM6Ly93d3cubGlmZWNhcmVzZXJ2aWNlcy1zZW5pb3JsaXZpbmcuY29tLw%3D%3D; __insp_targlpt=RW5oYW5jaW5nIFNlbmlvciBMaXZpbmcgRXhwZXJpZW5jZXMgfCBMaWZlIENhcmUgU2VydmljZXM%3D; _fbp=fb.1.1590408589954.63631529; __insp_norec_sess=true; hustle_module_show_count-slidein-2=3; inc_optin_slide_in_long_hidden-2=2; _dc_gtm_UA-7355654-8=1; _gat_UA-7355654-8=1; __insp_slim=1590408877184',
    #   'Origin': 'https://www.lifecareservices-seniorliving.com',
    #   'Referer': 'https://www.lifecareservices-seniorliving.com/find-a-community/',
    #   'Sec-Fetch-Dest': 'empty',
    #   'Sec-Fetch-Mode': 'cors',
    #   'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    #   'X-Requested-With': 'XMLHttpRequest',
    #   'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data = data).json()
    for ut in response['results']:
        soup1 = BeautifulSoup(ut['html'], "html5lib")
        for data in soup1.find_all("div",{"class":"cmnty-results-address"}):
            full = list(data.find("p",{"class":"address"}).stripped_strings)
            if full[0]=="Information Center":
                del full[0]
            city = list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[0]
            state= list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[-1].strip().split(" ")[0]
            zipp = list(data.find("p",{"class":"address"}).stripped_strings)[-1].split(",")[-1].strip().split(" ")[-1]
            street_address = ' '.join(full[:-1])
            location_name=data.find("h5",{"class":"cmnty-results-item-heading"}).text.strip()
            phone = list(data.stripped_strings)[-2].replace("Chicago,       IL","<MISSING>").replace("Austin,       TX       78731","<MISSING>").replace("West Lafayette,       IN       47906-1431","<MISSING>").replace("Wheaton,       IL       60187","<MISSING>").replace("Bridgewater,       NJ       08807","<MISSING>").replace("Atchison,       KS       66002","<MISSING>")
            # print(phone)
            try:
                page_url =(data.find("h5",{"class":"cmnty-results-item-heading"}).find("a")['href'])
            except:
                page_url="<MISSING>"
            latitude = ut['latitude']
            # print(latitude)
            longitude = ut['longitude']
            store_number="<MISSING>"
            location_type="<MISSING>"
       
            hours_of_operation="<MISSING>"
            store = ["https://www.lifecareservices-seniorliving.com", location_name, street_address.encode('ascii', 'ignore').decode('ascii').strip(), city, state, zipp.replace("IL","<MISSING>"), country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            # if store[2] in addresses:
            #     continue
            # addresses.append(store[2])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
