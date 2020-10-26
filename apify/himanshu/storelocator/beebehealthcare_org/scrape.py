import csv
from sgrequests import SgRequests
import requests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('beebehealthcare_org')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }

    base_url = "http://whywaitintheer.com/"     
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    url = "https://www.beebehealthcare.org/views/ajax"

    querystring = {"_wrapper_format":"drupal_ajax"}

    for i in range(0,12):
        payload = "view_name=location_terms&view_display_id=locations_land&view_dom_id=acb5a338c9a446cd24e401901e6d1b1daeb03095430e5094fef24354ffde2096&pager_element=0&selector=.js-view-dom-id-acb5a338c9a446cd24e401901e6d1b1daeb03095430e5094fef24354ffde2096&type=All&spec=All&proxi_s%5Bvalue%5D=9000000&page="+str(i)+"&_drupal_ajax=1&ajax_page_state%5Btheme%5D=particle&ajax_page_state%5Blibraries%5D=better_exposed_filters%2Fauto_submit%2Cbetter_exposed_filters%2Fgeneral%2Cblazy%2Fload%2Ccalendar%2Fcalendar.theme%2Ccore%2Fhtml5shiv%2Cgeofield_map%2Fgeofield_google_map%2Cgeofield_map%2Fgeojson%2Cgeofield_map%2Foverlappingmarkerspiderfier%2Cgutenberg%2Fblocks-view%2Cinclind_gutenberg_blocks%2Fblock-view%2Cparticle%2Fcontainer%2Cparticle%2Fcore%2Cparticle%2Flocations%2Cparticle%2Fsitewide%2Cparticle%2Ftypeahead_js%2Cpdm%2Fdrupal.pdm%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            }

        response = requests.post(url, data=payload, headers=headers, params=querystring)
        for data in json.loads(response.text):
            if "data" in data:
                soup = BeautifulSoup(data['data'],"lxml")
                for link  in soup.find_all("div",{"class":"location-info col"}):
                    page_url = "https://www.beebehealthcare.org"+link.find("a")['href']
                    r1 = requests.get(page_url)
                    soup1 = BeautifulSoup(r1.text,"lxml")
                    josn_data =json.loads(soup1.find("script",{"type":"application/ld+json"}).text)
                    street_address = josn_data['address']['streetAddress']
                    city = josn_data['address']['addressLocality']
                    state = josn_data['address']['addressRegion']
                    zipp = josn_data['address']['postalCode']
                    latitude = josn_data['geo']['latitude']
                    longitude = josn_data['geo']['longitude']
                    phone = josn_data['telephone'].strip()
                    if phone:
                        phone = phone
                    else:
                        phone = "<MISSING>"
                    try:
                        location_name = soup1.find("h1",{"class":"mb-4 h2"}).text.strip()
                    except:
                        location_name = "<MISSING>"
                    hours_of_operation =  "<MISSING>"
                    try:
                        hours_of_operation = " ".join(list(soup1.find("div",{"class":"hours-section"}).stripped_strings))
                    except:
                        hours_of_operation = "<MISSING>"

                    store=[]
                    store.append("https://www.beebehealthcare.org")
                    store.append(location_name)
                    store.append(street_address.split("Floor")[0].split("Suite")[0].replace(",",''))
                    store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
                    store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
                    store.append(zipp if zipp else "<MISSING>")   
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(latitude )
                    store.append(longitude )
                    store.append(hours_of_operation.strip().replace('HOURS','').encode('ascii', 'ignore').decode('ascii').strip())
                    store.append(page_url)
                    #logger.info("data==="+str(store))
                    #logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

                    yield store
                

                


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
