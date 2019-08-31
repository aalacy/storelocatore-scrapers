import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # print("soup ===  first")

    base_url = "https://www.ubs.com"
    # r = requests.get("https://www.ubs.com/locations/_jcr_content.lofisearch?a=bound&l=en&ucountry=ch&swlat=21.870172551137664&swlong=136.36625000000004&nelat=52.112245213927324&nelong=32.303750000000036&lat=37.09024&long=-95.71289100000001&searchCountry=US&o=100", headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")

    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "ubs"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    total_hits = 20
    lastHit = 0

    while total_hits == 20:
        r = requests.get(
            "https://www.ubs.com/locations/_jcr_content.lofisearch?a=bound&l=en&ucountry=ch&swlat=21.870172551137664&swlong=136.36625000000004&nelat=52.112245213927324&nelong=32.303750000000036&lat=37.09024&long=-95.71289100000001&searchCountry=US&o=" + str(
                lastHit), headers=headers)
        json_data = r.json()

        # firstHit = json_data['hits']['firstHit']
        lastHit = json_data['hits']['lastHit']
        total_hits = json_data['hits']['totalHits']
        for json_item in json_data['hits']['hits']:
            street_address = json_item['fields']['bu_podAddress'][0].split(',')[0]
            city = json_item['fields']['bu_city'][0].split(',')[0]
            location_name = city
            location_type = "ubs_" + json_item['fields']['pod_locationType'][0]
            latitude = json_item['fields']['latitude'][0]
            longitude = json_item['fields']['longitude'][0]

            temp_zipp = json_item['fields']['bu_podAddress'][0].split(',')[-1].strip().split(' ')[-1]
            if any(char.isdigit() for char in temp_zipp):
                if temp_zipp.isdigit() or len(temp_zipp) == 10:
                    zipp = temp_zipp
                    state = json_item['fields']['bu_podAddress'][0].split(',')[-1].strip().split(' ')[-2]
                else:
                    zipp = ' '.join(json_item['fields']['bu_podAddress'][0].split(',')[-1].strip().split(' ')[-2:])
                    state = json_item['fields']['bu_podAddress'][0].split(',')[-1].strip().split(' ')[-3]
            else:
                zipp = '<MISSING>'

            partial_url = json_item['fields']['id'][0].replace('/', '_')
            hours_url = 'https://www.ubs.com/locations/_jcr_content.location.' + partial_url + '.en'

            # print('hours_url === ' + hours_url)

            r_hours = requests.get(hours_url, headers=headers)

            # print('r_hours source Data === ' + str(r_hours.json()))
            # print('fields ==== ' + str(json_item['fields']))

            json_hours_data = r_hours.json()

            hours_of_operation = ""
            phone = json_hours_data['telephoneNumber']

            if len(phone) == 0:
                phone = '<MISSING>'

            if json_hours_data['busOpenHrs'] is not None and json_hours_data['busOpenHrs'][
                'businessOpeningHours'] is not None and len(json_hours_data['busOpenHrs']['businessOpeningHours']) > 0:
                hours_list = json_hours_data['busOpenHrs']['businessOpeningHours'][0]['collapsedDays']

                if hours_list is not None:
                    for hours_item in hours_list:
                        if len(hours_item['collapsedHrs']) > 0:
                            hours_of_operation += hours_item['dayRange'] + ' : ' + '- '.join(
                                hours_item['collapsedHrs']) + ', '
                        else:
                            hours_of_operation += hours_item['dayRange'] + ' : ClOSED, '
                        # print('hours_url ===== '+ str(hours_item))

            if len(hours_of_operation) == 0:
                hours_of_operation = '<MISSING>'

            # print('hours_of_operation ===== ' + str(hours_of_operation))

            if '<MISSING>' not in zipp:
                if len(zipp.replace(' ', '').replace('-','')) == 9 or len(zipp.replace(' ', '').replace('-','')) == 5:
                    country_code = "US"
                elif len(zipp.replace(' ', '')) == 6:
                    country_code = 'CA'
                elif len(zipp.replace(' ', '')) == 7:
                    country_code = 'UK'
                else:
                    country_code = "UK"

            else:
                country_code = 'US'

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            if 'UK' not in country_code:
                return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
