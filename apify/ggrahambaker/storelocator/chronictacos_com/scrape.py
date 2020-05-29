import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

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
    locator_domain = 'https://www.chronictacos.com/'
    ext_arr = ['locations', 'canada-locations']

    page = session.get(locator_domain + ext_arr[0])
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    divs = soup.find_all('div', {'class': 'dynamicColumn span4'})

    all_store_data = []
    for div in divs:
        ps = div.find_all('p', {'class': 'fp-el'})

        if len(ps) is not 0:

            if len(ps) == 2:
                if '104 Stadium Drive' in ps[1].text:
                    location_name = 'UNC CHAPEL HILL FOOTBALL'
                    brs = ps[1].find_all('br')
                    street_address = brs[0].previousSibling

                    city, state, zip_code = addy_extractor(brs[1].previousSibling)

                    phone_number = '<MISSING>'
                    country_code = 'US'
                    store_number = '<MISSING>'
                    location_type = '<MISSING>'
                    lat = '<MISSING>'
                    longit = '<MISSING>'
                    hours = '<MISSING>'
                    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                                  store_number, phone_number, location_type, lat, longit, hours]
                    print(store_data)
                    all_store_data.append(store_data)

                elif '300 Skipper' in ps[1].text:
                    location_name = 'UNC CHAPEL HILL BASKETBALL'
                    brs = ps[1].find_all('br')
                    street_address = brs[0].previousSibling

                    city, state, zip_code = addy_extractor(brs[1].previousSibling)

                    phone_number = '<MISSING>'
                    country_code = 'US'
                    store_number = '<MISSING>'
                    location_type = '<MISSING>'
                    lat = '<MISSING>'
                    longit = '<MISSING>'
                    hours = '<MISSING>'
                    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                                  store_number, phone_number, location_type, lat, longit, hours]
                    print(store_data)
                    all_store_data.append(store_data)

                elif '235 Ridge Road' in ps[1].text:
                    location_name = 'UNC CHAPEL HILL BASEBALL'
                    brs = ps[1].find_all('br')
                    street_address = brs[0].previousSibling

                    city, state, zip_code = addy_extractor(brs[1].previousSibling)

                    phone_number = '<MISSING>'
                    country_code = 'US'
                    store_number = '<MISSING>'
                    location_type = '<MISSING>'
                    lat = '<MISSING>'
                    longit = '<MISSING>'
                    hours = '<MISSING>'
                    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                                  store_number, phone_number, location_type, lat, longit, hours]
                    print(store_data)
                    all_store_data.append(store_data)

            p = ps[0]

            brs = p.find_all('br')
            if len(brs) == 2:
                street_address = brs[0].previousSibling.strip()
                location_name = street_address
                if 'Angel Stadium of Anaheim' in street_address:
                    street_address = brs[1].previousSibling
                    location_name = street_address
                    city, state, zip_code = addy_extractor(brs[1].nextSibling)
                    phone_number = '<MISSING>'
                elif '3780 South Las Vegas Boulevard' in street_address:
                    city, state, zip_code = addy_extractor(brs[1].previousSibling)
                    phone_number = '<MISSING>'
                elif '9424 Falls of Neuse ' in street_address:
                    city_and_state = brs[1].previousSibling.strip().split(' ')
                    city = city_and_state[0]
                    state = city_and_state[1]
                    zip_code = '<MISSING>'
                    phone_number = brs[1].nextSibling.strip()
                else:
                    city, state, zip_code = addy_extractor(brs[1].previousSibling)
                    phone_number = brs[1].nextSibling.strip()
            elif len(brs) == 1:
                if len(p.find_all('span')) == 2:
                    if 'Kapahulu' in p.find_all('span')[0].text:
                        street_address = p.find_all('span')[0].text
                        location_name = street_address
                        city, state, zip_code = addy_extractor(p.find_all('span')[1].text)
                    elif '11510 Fashion' in p.find_all('span')[0].text:
                        br = p.find_all('span')[0].find('br')
                        street_address = br.previousSibling
                        location_name = street_address
                        br_arr = br.nextSibling.strip().split(',')
                        city = br_arr[0]
                        state = br_arr[1]
                        zip_code = p.find_all('span')[1].text
                        phone_number = '<MISSING>'
                else:
                    street_address = brs[0].previousSibling
                    location_name = street_address
                    if 'Fashion Court' in street_address:
                        address = brs[0].nextSibling.split(',')
                        city = address[0].strip()
                        state = address[1].strip()
                        zip_code = p.find_all('span')[1].text.strip()
                        phone_number = '<MISSING>'
                    elif 'Forestville' in street_address:
                        addy_split = street_address.split(',')
                        street_address = addy_split[0]
                        location_name = street_address
                        city = addy_split[1].strip()
                        state = addy_split[2].strip().split(' ')[0]
                        zip_code = addy_split[2].strip().split(' ')[1]
                        phone_number = brs[0].nextSibling
                    elif 'Eva S' in street_address:
                        city, state, zip_code = addy_extractor(brs[0].nextSibling)
                        phone_number = '<MISSING>'
                    else:
                        city, state, zip_code = addy_extractor(brs[0].nextSibling)
                        phone_number = div.find_all('p', {'class': 'fp-el'})[1].text

            elif len(brs) == 3:
                street_address = brs[0].previousSibling + ' ' + brs[1].previousSibling[:-1]
                location_name = street_address
                city, state, zip_code = addy_extractor(brs[2].previousSibling)
                phone_number = brs[2].nextSibling
            elif len(brs) == 0:
                p = div.find_all('p', {'class': 'fp-el'})

                street_address = p[0].text
                location_name = street_address
                city, state, zip_code = addy_extractor(p[1].text)
                phone_number = p[2].text.replace('Store Phone:', '')

            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            page = session.get('http:' + div.find('a', {'class': 'btn'})['href'])
            assert page.status_code == 200
            soup = BeautifulSoup(page.content, 'html.parser')

            hour_div = soup.find('div', {'class': 'article-desc'})

            if hour_div is None:
                hours = '<MISSING>'
            elif hour_div.find('h3') == None:
                hours = '<MISSING>'
            elif 'HOURS' in hour_div.find('h3').text or 'Hours' in hour_div.find('h3').text:
                ps = hour_div.find_all('p')
                hours = ''
                for p in ps:
                    pattern = re.compile("((\d+)\:(\d+))")
                    if pattern.search(p.text):
                        hours += p.text + ' '
                    elif ' - ' in p.text:
                        hours += p.text + ' '

            else:
                hours = '<MISSING>'
            phone_number = phone_number.replace('Phone.', '').replace('\xa0', '').strip()
            if hours == '':
                hours = '<MISSING>'

            hours = hours.replace('Â\xa0', ' ')

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]

            all_store_data.append(store_data)

    # canada now!
    page = session.get(locator_domain + ext_arr[1])
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, 'html.parser')

    divs = soup.find_all('div', {'class': 'dynamicColumn span4'})

    for div in divs:
        stores = div.find_all('div', {'class': 'mod_article'})
        for store in stores:
            p = store.find('p', {'class': 'fp-el'})
            brs = p.find_all('br')

            if len(brs) == 1:
                street_address = brs[0].previousSibling
                location_name = street_address
                commas = brs[0].nextSibling.split(',')
                city = commas[0]
                state_zip = commas[1].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1] + ' ' + state_zip[2]
                phone_number = '<MISSING>'
            else:
                street_address = brs[0].previousSibling
                location_name = street_address
                if '2765 Main' in street_address:
                    street_address += ' ' + brs[1].previousSibling

                    commas = brs[1].nextSibling.split(',')
                    city = commas[0]

                    city.split(' ')[1]
                    state_zip = commas[1].strip().split(' ')

                    state = city.split(' ')[1]
                    city = city.split(' ')[0]
                    zip_code = state_zip[1] + ' ' + state_zip[2]

                    phone_number = '<MISSING>'

                else:
                    commas = brs[0].nextSibling.split(',')
                    city = commas[0]
                    state_zip = commas[1].strip().split(' ')
                    state = state_zip[0]
                    if '-' in commas[1]:
                        zip_code = state_zip[1].replace('-', ' ')
                    else:
                        zip_code = state_zip[1] + ' ' + state_zip[2]

                    phone_number = brs[1].nextSibling

            country_code = 'CA'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            page = session.get('http:' + div.find('a', {'class': 'btn'})['href'])
            assert page.status_code == 200
            soup = BeautifulSoup(page.content, 'html.parser')

            hour_div = soup.find('div', {'class': 'article-desc'})
            if hour_div.find('h3') == None:
                hours = '<MISSING>'
            elif 'HOURS' in hour_div.find('h3').text or 'Hours' in hour_div.find('h3').text:
                ps = hour_div.find_all('p')
                hours = ''
                for p in ps:
                    pattern = re.compile("((\d+)\:(\d+))")
                    if pattern.search(p.text):
                        hours += p.text + ' '
                    elif ' - ' in p.text:
                        hours += p.text + ' '

            else:
                hours = '<MISSING>'
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
