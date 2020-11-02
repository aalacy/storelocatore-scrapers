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

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    url = 'https://hosted.where2getit.com/quiktrip/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E82C11D38-0EC6-11E0-8AD9-4C59241F5146%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E10000%3C%2Flimit%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3Eiowa%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E5000%3C%2Fsearchradius%3E%3Cwhere%3E%3Ctravelcenter%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftravelcenter%3E%3Ctruckdiesel%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftruckdiesel%3E%3Ce15%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fe15%3E%3Cautodiesel%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fautodiesel%3E%3Cspecialtydrinks%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fspecialtydrinks%3E%3Cgen3%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fgen3%3E%3Chotandfreshpretzels%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fhotandfreshpretzels%3E%3Chotsandwiches%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fhotsandwiches%3E%3Cxlpizza%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fxlpizza%3E%3Cpersonalpizzas%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpersonalpizzas%3E%3Cnoethanol%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fnoethanol%3E%3Ccertifiedscales%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcertifiedscales%3E%3Cdef%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fdef%3E%3Cfrozentreats%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffrozentreats%3E%3Cfreshbrewedtea%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffreshbrewedtea%3E%3Cfrozendrinks%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffrozendrinks%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E'
    r = session.get(url, headers = HEADERS)

    soup = BeautifulSoup(r.content, 'html.parser')
    locs = soup.find_all('poi')
    locator_domain = 'https://www.quiktrip.com/'
    all_store_data = []
    for loc in locs:
        location_name = loc.find('name').text
        
        store_number = location_name.split('#')[1]
        
        street_address = loc.find('address1').text
        city = loc.find('city').text
        state = loc.find('state').text
        zip_code = loc.find('postalcode').text
        phone_number = loc.find('phone').text
        
        lat = loc.find('latitude').text
        longit = loc.find('longitude').text
        
        country_code = 'US'
        location_type = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
