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

    locator_domain = 'http://pumpandpantry.com/' 
    ext = 'locations/all_locations.php'

    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')
    ## get the hours
    stores = soup.find_all('td', {'width': '175'})
    hours_arr = []
    for st in stores:
        hours_arr.append(st.text)

    stores = soup.find('table')

    all_store_data = []
    rows = soup.find_all('tr')
    id_arr = []
    for row in rows[1: ]:
        cols = row.find_all('td')
        if len(cols) > 0:
            store_number = cols[0].text
                
            id_arr.append(store_number)
            
            location_name = cols[2].text
            street_address = cols[2].text

            city = cols[3].text
            state = cols[4].text
            zip_code = cols[5].text

            phone_number = cols[6].text
        
        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        long = '<MISSING>'
        hours = '<MISSING>'
        
        # done parsing, lets push it to an array
        # should be like this
        # locator_domain, location_name, street_address, city, state, zip, country_code,
        # store_number, phone, location_type, latitude, longitude, hours_of_operation
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, long, hours ]

        all_store_data.append(store_data)

    ## put the hours back in
    for i, data in enumerate(all_store_data):
        data[-1] = hours_arr[i]
         
    to_del = 100000
    for i, store in enumerate(all_store_data):
        #print(store[7])
        if store[7] in id_arr:
            to_del = i
        else:
            id_arr.append(store[7])
        
    del all_store_data[to_del]

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
