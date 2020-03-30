import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.joann.com"

    while zip_code:
        result_coords = []

        # print("zip_code === "+zip_code)

        location_url = 'https://hosted.where2getit.com/joann/mystore/ajax?&xml_request=<request><appkey>53EDE5D6-8FC1-11E6-9240-35EF0C516365</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>250</limit><geolocs><geoloc><addressline>'+str(zip_code)+'</addressline><longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>30|50|100|250</searchradius><where><new_in_store_meet_up><eq></eq></new_in_store_meet_up><or><customframing><eq></eq></customframing><edu_demos><eq></eq></edu_demos><busykids><eq></eq></busykids><buyonline><eq></eq></buyonline><vikingsewinggallery><eq></eq></vikingsewinggallery><project_linus><eq></eq></project_linus><sewing_studio><eq></eq></sewing_studio><store_features><eq></eq></store_features><petfriendly><eq></eq></petfriendly><glowforge><eq></eq></glowforge><custom_shop><eq></eq></custom_shop></or></where></formdata></request>'
        try:
            r = session.get(location_url,headers=headers)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        # print("location_url ==== ",soup)
        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
        current_results_len = len(soup.find_all("poi"))    # it always need to set total len of record.
        locator_domain = base_url
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
        # print(soup.find_all("poi"))
        for poi in soup.find_all("poi"):
          
            location_name1 = poi.find("address2").text
            if location_name1!='':
                location_name = poi.find("address2").text
            else:
                location_name=poi.find("name").text.replace('Fabrics and Crafts','')   

            street_address = poi.find("address1").text
         
           
            hours_of_operation =' Sunday ' +  poi.find("sunopen").text +  ' ' + poi.find("sunclose").text +' Monday ' + poi.find("monopen").text +  ' ' + poi.find("monclose").text +' Tuesday '+  poi.find("tueopen").text +  ' ' + poi.find("tueclose").text  +' Wednesday '+  poi.find("wedopen").text +  ' ' + poi.find("wedclose").text  +' Thursday '+  poi.find("thuopen").text +  ' ' + poi.find("thuclose").text  +' Friday '+  poi.find("friopen").text +  ' ' + poi.find("friclose").text +' Saturday '+  poi.find("satopen").text +  ' ' + poi.find("satclose").text
            country_code = poi.find("country").text
            latitude = poi.find("latitude").text
            longitude = poi.find("longitude").text
            phone = poi.find("phone").text
            zipp = poi.find("postalcode").text
            state = poi.find("state").text
            # do your logic.
            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address.lstrip().lstrip(), soup.find("city").text.strip(), state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation.lstrip().lstrip(),'<MISSING>']
            if store[2] + store[-3] in addresses:
                continue
            addresses.append(store[2] + store[-3])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
            # return_main_object.append(store)

        # yield store
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
