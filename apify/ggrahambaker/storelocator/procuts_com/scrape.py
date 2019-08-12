import csv
import requests
from bs4 import BeautifulSoup


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return city, state, zip_code


def fetch_data():

    locator_domain = 'https://www.procuts.com/'

    ext = 'salonlocator/default.asp?state=all&city=BROWNSVILLE'
    ext2 = 'salonlocator/default.asp?state=all&city=CORPUS CHRISTI'


    to_scrape1 = locator_domain + ext
    page1 = requests.get(to_scrape1)
    assert page1.status_code == 200
    page1_string = page1.content.decode("utf-8")

    start_idx = page1_string.find('showMarker = false;') + len('showMarker = false;')
    end_idx = page1_string.find('MapDefaultZoom')

    coord_string = page1_string[start_idx:end_idx - 3]

    lat_start = coord_string.find('singlelat') + len('singlelat = ')
    lat = coord_string[lat_start:lat_start+5]
    long_start = coord_string.find('singlelon') + len('singlelon = ')
    longit = coord_string[long_start:long_start + 6]
    soup = BeautifulSoup(page1.content, 'html.parser')
    store = soup.find('div', {'class': 'result_LocationContainer'})

    location_name = store.find('div', {'class': 'result_MallName'}).text

    street_address = store.find('div', {'class': 'result_Street'}).text
    city, state, zip_code = addy_extractor(store.find('div', {'class': 'result_Location'}).text)
    phone_number = store.find('div', {'class': 'result_Phone'}).text

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    hours = '<MISSING>'

    sunrise_plaza = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]


    to_scrape2 = locator_domain + ext2
    page2 = requests.get(to_scrape2)
    assert page2.status_code == 200
    page2_string = page2.content.decode("utf-8")
    print('----2-----\n\n')
    #print(page2_string)
    start_idx = page2_string.find('showMarker = false;') + len('showMarker = false;')
    end_idx = page2_string.find('MapDefaultZoom')

    coord_string = page2_string[start_idx:end_idx - 3]
    print(coord_string)
    lat_start = coord_string.find('singlelat') + len('singlelat = ')
    # print(coord_string[lat_start:lat_start+5])
    lat = coord_string[lat_start:lat_start + 5]
    long_start = coord_string.find('singlelon') + len('singlelon = ')
    # print(coord_string[long_start:long_start + 6])
    longit = coord_string[long_start:long_start + 6]
    soup = BeautifulSoup(page2.content, 'html.parser')
    store = soup.find('div', {'class': 'result_LocationContainer'})

    location_name = store.find('div', {'class': 'result_MallName'}).text

    street_address = store.find('div', {'class': 'result_Street'}).text
    city, state, zip_code = addy_extractor(store.find('div', {'class': 'result_Location'}).text)
    phone_number = store.find('div', {'class': 'result_Phone'}).text

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    hours = '<MISSING>'

    cim_center = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]

        
    all_store_data = [sunrise_plaza, cim_center]
    
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
