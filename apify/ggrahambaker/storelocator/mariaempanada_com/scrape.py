import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'http://mariaempanada.com/' 
    ext = 'contact/'
    r = session.get(locator_domain + ext, headers = HEADERS)


    soup = BeautifulSoup(r.content, 'html.parser')
    maps = soup.find_all('div', {'class': 'google_map_holder'})


    all_store_data = []
    for map_div in maps:
        main = map_div.parent
        location_name = main.find('h4').text
        
        location_type = main.find('h6').text
        more_info = main.find_all('div', {'class': 'wpb_text_column'})[1]
        ps = more_info.find_all('p')
        street_address = ps[0].text.strip()
        city, state, zip_code = addy_ext(ps[1].text.strip())    
        if len(ps) == 4:
            phone_number = '<MISSING>'
        else:
            phone_number = ps[2].text.strip()
        
        hours = ps[-1].text.strip()
        
        
        country_code = 'US'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = '<MISSING>'
        
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        print(store_data)
        all_store_data.append(store_data)






    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
