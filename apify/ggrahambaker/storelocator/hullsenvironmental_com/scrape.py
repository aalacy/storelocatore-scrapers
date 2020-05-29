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

def fetch_data():
    # return 2D array to be written to csv
    locator_domain = 'https://www.hullsenvironmental.com/' 
    ext = 'locations'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    div = soup.find('div', {"id": "comp-jn2281qa"})
    
    ps = div.find_all('p')
    ## inconsistent formatting
    case_1 = [[ps[0], ps[1], ps[2]], [ps[4], ps[5], ps[6]], [ps[8], ps[9], ps[10]] ]
    case_2 = [[ps[12], ps[13], ps[14], ps[15]], [ps[18], ps[19], ps[20], ps[21]], [ps[23], ps[24], ps[25], ps[26]] ]
    case_3 = [ps[29], ps[30]]

    all_store_data = []

    ## case 1
    for case in case_1:
        location_name = case[0].text
        address = case[1].text.split('\n')
        street_address = address[0]
        address_other = address[1].split(',')
        city = address_other[0]
        add_arr = address_other[1].split(' ')
        state = add_arr[1]
        zip_code = add_arr[2].strip()
        phone_number_temp = case[2].text.split('\n')
        
        phone_number = phone_number_temp[0].split(': ')[1]
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    ## case 2
    for case in case_2:
        location_name = case[0].text
        street_address = case[1].text
        
        address_other = case[2].text.split(',')
        city = address_other[0]

        answer = address_other[1].strip()
        add_arr = answer.split(' ')
        if len(add_arr) == 1:
            state = add_arr[0][0:2]
            zip_code = add_arr[0][-5:]
        else:
            state = add_arr[0]
            zip_code = add_arr[1]
        
        phone_number = case[3].text.split(': ')[1]
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        
    ## case 3
    location_name = case_3[0].text
    info = case_3[1].text.split('\n')
    street_address = info[0]
    address_other = info[1].split(',')
    city = address_other[0]

    answer = address_other[1].strip()
    add_arr = answer.split(' ')
    state = add_arr[0]
    zip_code = add_arr[1].strip()
    phone_number = info[2].split(': ')[1]

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'
    hours = '<MISSING>'

    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                 store_number, phone_number, location_type, lat, longit, hours ]
    all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
