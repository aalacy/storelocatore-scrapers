import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('extremepita_com')
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
    locator_domain = "https://extremepita.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    url = "https://extremepita.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"

    querystring = {"wpml_lang":"en","t":"1572423853390"}

    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache"
        }

    r = session.get(url, headers=headers, params=querystring)
  
    soup = BeautifulSoup(r.text,'lxml')
    for store in  soup.find('store').find_all('item'):

        location_name = store.find('location').text.replace('&amp;','and').replace('&#44;',",").replace('&#39;',"'")
        store_number = store.find('contactus').nextSibling.text.strip()
        address = store.find('address')
        list_address = list(address.stripped_strings)
        tag_address= " ".join(list_address).split(',')
        if len(tag_address) > 2:
            st_add = " ".join(tag_address[:-1]).split()
            street_address = " ".join(st_add[:-1]).replace('Red','').strip()
            if "Deer" != st_add[-1]:
                city =st_add[-1].strip()
            else:
                city = " ".join(st_add[-2:]).strip()
            state = tag_address[-1].split()[0].strip()
            zipp = " ".join(tag_address[-1].split()[-2:]).strip()

        else:
            zipp = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(tag_address[-1]))[0]
            if len(tag_address[-1].split()) >2:
                state =  " ".join(tag_address[-1].split()[:-2])
            else:
                state = tag_address[-1].split()[0].strip()

            if len(tag_address[0].split('  ')) > 2:
                street_address = " ".join(tag_address[0].split('  ')[:-1]).strip()
            else:
                street_address=tag_address[0].split('  ')[0]

            city = tag_address[0].split('  ')[-1].strip()
            tag_phone = store.find('telephone')
            list_phone = list(tag_phone.stripped_strings)
            if list_phone == []:
                phone  = "<MISSING>"
            else:
                phone= list_phone[0].split(';')[0]
            latitude = store.find('latitude').text.strip()
            longitude = store.find('longitude').text.strip()
            country_code = "CA"
            hours = store.find('exturl').nextSibling
            soup_hours = BeautifulSoup(hours.text,'lxml')
            h = []
            for hr in soup_hours.find_all('p'):
                hour = hr.text.replace('\n' ,'  ')
                h.append(hour)
            hours_of_operation = "   ".join(h).replace('&','-').replace('\r','-').strip().replace("Call 403-945-0178 for weekend availability","")
            page_url = "https://extremepita.com/locations/"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
