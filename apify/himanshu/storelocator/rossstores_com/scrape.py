import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rossstores_com')






session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    
    return_main_object = []
    addresses = []
    store_name=[]
    store_detail=[]
    result_coords = []
    MAX_RESULTS = 1000
    MAX_DISTANCE = 5000
    current_results_len = 0  # need to update with no of count.
  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    zip_code = search.next_zip()
    while zip_code:
        # logger.info("zips === " + str(zip_code))
        r = session.get('https://hosted.where2getit.com/rossdressforless/2014/ajax?xml_request=<request><appkey>097D3C64-7006-11E8-9405-6974C403F339</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>'+str(MAX_RESULTS)+'</limit><geolocs><geoloc><addressline>'+str(zip_code)+'</addressline><country>US</country></geoloc></geolocs><searchradius>'+str(MAX_DISTANCE)+'</searchradius></formdata></request>',
            headers=headers)
        
        soup= BeautifulSoup(r.text,"lxml")
        current_results_len = len(soup.find_all('poi'))
        for x in soup.find_all('poi'):
            locator_domain = 'https://www.rossstores.com/'
            location_name = x.find('name').text.strip()
            street_address = x.find('address1').text.strip()
            city = x.find('city').text.strip()
            state = x.find('state').text.strip()
            zip = x.find('postalcode').text.strip()
            country_code = x.find('country').text.strip()
            store_number = '<MISSING>'
            phone = x.find('phone').text.strip()
            phone = x.find('phone').text.strip()
            location_type = '<MISSING>'
            latitude = x.find('latitude').text.strip()
            longitude = x.find('longitude').text.strip()
            result_coords.append((latitude, longitude))
            if street_address in addresses:
                continue
            addresses.append(street_address)
            hours_of_operation = 'sunday:' + x.find('sunday').text.strip() + ' monday : ' + x.find('monday').text.strip() + ' tuesday :' + x.find('tuesday').text.strip() + ' wednesday:' + x.find('wednesday').text.strip() + ' tuesday: ' + x.find('tuesday').text.strip() + ' friday: ' + x.find('friday').text.strip() + ' saturday: ' + x.find('saturday').text.strip()
            page_url = "https://hosted.where2getit.com/rossdressforless/2014/ajax?xml_request=<request><appkey>097D3C64-7006-11E8-9405-6974C403F339</appkey><formdata id='locatorsearch'><dataview>store_default</dataview><limit>1000</limit><geolocs><geoloc><addressline>"+str(zip_code)+"</addressline><country>US</country></geoloc></geolocs><searchradius>100</searchradius></formdata></request>"
            store = []
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
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append('<MISSING>')
            # logger.info("===", str(store))
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()





