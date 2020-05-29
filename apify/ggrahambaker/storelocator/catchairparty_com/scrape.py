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

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1].replace('.', '')
        zip_code = prov_zip[2]

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://catchairparty.com/'
    ext = 'locations/'
    page = session.get(locator_domain + ext)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    divs = soup.find_all('div', {'class': 'location_btm'})

    all_store_data = []
    for div in divs:
        location_name = div.find('h4').text

        link = div.find('a')['href']

        sub_page = session.get(link)
        assert sub_page.status_code == 200

        new_soup = BeautifulSoup(sub_page.content, 'html.parser')

        about = new_soup.find_all('div', {'class': 'about_catch_cnt'})
        brs = about[0].find_all('br')
        if len(brs) == 2:
            split_arr = about[0].text.strip().split('\n')
            if 'Snellville' in split_arr[0]:
                comma = split_arr[1].split(',')
                street_address = comma[0]
                city = comma[1]
                state_zip = comma[2].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
                phone_number = split_arr[2]
            elif 'Sandy Springs' in split_arr[0]:
                idx = split_arr[1].find('c-212')
                street_address = split_arr[1][:idx + 5].strip()
                address = split_arr[1][idx + 6:]
                city, state, zip_code = addy_extractor(address)
                phone_number = split_arr[2]
            elif 'Paramus' in split_arr[0]:
                street_address = split_arr[2].replace('\r', '').strip()
                address = split_arr[3].split('\xa0')
                city = address[0][:-1]
                state = address[1]
                zip_code = address[2]
                phone_number = split_arr[-2]
            else:
                address = split_arr[2].split(',')
                if len(address) == 3:
                    street_address = address[0]
                    city = address[1].strip()
                    state_zip = address[2].strip().split(' ')
                    state = state_zip[0]
                    zip_code = state_zip[1]
                else:
                    idx = address[0].find('Rd')
                    street_address = address[0][:idx + 2].strip()
                    city = address[0][idx + 2:].strip()
                    state_zip = address[1].strip().split(' ')
                    state = state_zip[0]
                    zip_code = state_zip[1]
                phone_number = split_arr[-2]
        elif len(brs) == 3:
            info = about[0].text.strip().split('\n')
            street_address = info[2].replace('\r', '').replace('\xa0', '').strip()
            address = info[3].replace('\r', '')
            city, state, zip_code = addy_extractor(address)
            phone_number = info[4]
        else:
            info = about[0].text.strip().split('\n')
            street_address = info[2].replace('\r', '').replace('\xa0', '').strip()
            address = info[3].strip()
            city, state, zip_code = addy_extractor(address)
            phone_number = info[4]

        hours_un = about[1].text.replace('STORE HOURS', '').strip().replace('\r', '').split('\n')

        hours = ''
        for h in hours_un:
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
