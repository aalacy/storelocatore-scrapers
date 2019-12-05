import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://data.sfgov.org"


    data_len = 1
    index = 0
    total_length = 0

    while (data_len > 0):
        # location_url = 'https: // data.sfgov.org / api / id / g8m3 - pdis.json?$select = `ttxid`, `certificate_number`, `ownership_name`, `dba_name`, `full_business_address`, `city`, `state`, `business_zip`, `dba_start_date`, `dba_end_date`, `location_start_date`, `location_end_date`, `mailing_address_1`, `mail_city`, `mail_zipcode`, `mail_state`, `naic_code`, `naic_code_description`, `parking_tax`, `transient_occupancy_tax`, `lic`, `lic_code_description`, `supervisor_district`, `neighborhoods_analysis_boundaries`, `business_corridor`, `location` &$order = `ttxid` + ASC &$limit = 1000 &$offset = '+ str(index)
        location_url = 'https://data.sfgov.org/api/id/g8m3-pdis.json?$select=`ttxid`,`certificate_number`,`ownership_name`,`dba_name`,`full_business_address`,`city`,`state`,`business_zip`,`dba_start_date`,`dba_end_date`,`location_start_date`,`location_end_date`,`mailing_address_1`,`mail_city`,`mail_zipcode`,`mail_state`,`naic_code`,`naic_code_description`,`parking_tax`,`transient_occupancy_tax`,`lic`,`lic_code_description`,`supervisor_district`,`neighborhoods_analysis_boundaries`,`business_corridor`,`location`&$order=`ttxid`+ASC&$limit=1000&$offset=' + str(
            index)
        r = requests.get(location_url, headers=header).json()
        index += 1000
        data_len = len(r)
        total_length += data_len
        
        for idx, val in enumerate(r):
                try:

                    if 'dba_end_date' not in val:


                        locator_domain = base_url
                        location_name = " ".join(list(BeautifulSoup(val['ownership_name'],"lxml").stripped_strings))
                        street_address = val['full_business_address']
                        city = val['city']
                        state = val['state']
                        zip = val['business_zip']
                        store_number = '<MISSING>'
                        country_code = '<MISSING>'
                        phone = '<MISSING>'
                        location_type = '<MISSING>'
                        latitude = val['location']['coordinates'][1]
                        longitude = val['location']['coordinates'][0]
                        hours_of_operation = '<MISSING>'

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
                        yield store
                except:
                   
                    continue



def scrape():
    data = fetch_data()

    write_output(data)


scrape()
