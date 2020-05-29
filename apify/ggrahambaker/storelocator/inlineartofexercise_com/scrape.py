import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

## helper for fetch_data
def addy_maker(line):
    split = line.split(',')
    city = split[0]
    split2 = split[1].split(' ')
    state = split2[1]
    zip_code = split2[2].replace('\r', '')
    return city, state, zip_code

def fetch_data():

    locator_domain = 'https://inlineartofexercise.com/'

    to_scrape = locator_domain
    page = session.get(to_scrape)
    assert page.status_code == 200
    soup = BeautifulSoup(page.content, 'html.parser')

    tail = soup.find('div', {'class': 'textwidget'})
    #print(tail.text.split('\n'))
    tail_arr = tail.text.split('\n')

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'
    hours = '<MISSING>'

    city1, state1, zip_code1 = addy_maker(tail_arr[2])

    store_data1 = [locator_domain, tail_arr[0].replace('\r', ''), tail_arr[1].replace('\r', ''), city1, state1, zip_code1, country_code,
                     store_number, tail_arr[3].split(':')[1].strip(), location_type, lat, longit, hours ]

    city2, state2, zip_code2 = addy_maker(tail_arr[9])

    store_data2 = [locator_domain, tail_arr[7].replace('\r', ''), tail_arr[8].replace('\r', ''), city2, state2, zip_code2, country_code,
                     store_number, tail_arr[10].split(':')[1].strip(), location_type, lat, longit, hours ]

    city3, state3, zip_code3 = addy_maker(tail_arr[17])

    store_data3 = [locator_domain, tail_arr[14].replace('\r', ''), tail_arr[16].replace('\r', ''), city3, state3, zip_code3, country_code,
                     store_number, '<MISSING>', location_type, lat, longit, hours ]
    all_store_data = [store_data1, store_data2, store_data3]

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
