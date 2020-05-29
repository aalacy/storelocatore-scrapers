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

    locator_domain = 'http://ladiesworkoutexpress.com/'
    ext = 'findAClub.asp'

    to_scrape = locator_domain + ext
    print(to_scrape)
    page = session.get(to_scrape)
    assert page.status_code == 200

    all_store_data = []

    soup = BeautifulSoup(page.content, 'html.parser')
    div = soup.find_all('div', {"class": "grid-4-12"})

    ## first col, pretty normal
    ps = div[0].find_all('p')
    for p in ps[:9]:
        brs = p.find_all('br')
        street_address = brs[0].previousSibling.replace(',', '')
        location_name = street_address
        addy_info = brs[1].previousSibling.split(',')
        city = addy_info[0]
        addy_info2 = addy_info[1].split(' ')
        state = addy_info2[1]
        zip_code = addy_info2[2]
        phone_number = brs[2].previousSibling
        location_type = 'ladies workout express'
        country_code = 'US'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    #only 1 weird case
    ps = div[1].find_all('p')
    for p in ps:
        brs = p.find_all('br')
        street_address = brs[0].previousSibling.replace(',', '')
        location_name = street_address
        if len(brs) == 3:
            addy_info = brs[1].previousSibling.split(',')
            city = addy_info[0]

            addy_info2 = addy_info[1].split(' ')
            state = addy_info2[1]
            zip_code = addy_info2[2]
            phone_number = brs[2].previousSibling
        else:
            addy_info = brs[2].previousSibling.split(',')
            city = addy_info[0]

            addy_info2 = addy_info[1].split(' ')
            state = addy_info2[1]
            zip_code = addy_info2[2]
            phone_number = brs[3].previousSibling
        
        location_type = 'lady of america'
        country_code = 'US'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    ## extra info in 1 col
    ps = div[2].find_all('p')

    for p in ps[:-2]:
        brs = p.find_all('br')
        street_address = brs[0].previousSibling.replace(',', '')
        location_name = street_address 
        if len(brs) == 3:
            addy_info = brs[1].previousSibling.split(',')
            city = addy_info[0]
            
            addy_info2 = addy_info[1].split(' ')
            state = addy_info2[1]
            zip_code = addy_info2[2]
            phone_number = brs[2].previousSibling
        else:
            street_address += brs[1].previousSibling.replace(',', '')
            addy_info = brs[2].previousSibling.split(',')
            city = addy_info[0].strip()
            
            addy_info2 = addy_info[1].split(' ')
            state = addy_info2[1]
            zip_code = addy_info2[2]
            phone_number = brs[3].previousSibling

        location_type = 'loa fitness for women'
        
        country_code = 'US'
        store_number = '<MISSING>'
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
