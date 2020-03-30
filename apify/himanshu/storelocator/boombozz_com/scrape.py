import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

session = SgRequests()

requests.packages.urllib3.disable_warnings()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://boombozz.com/"
    loacation_url = 'https://boombozz.com/locations/'
    r = session.get(loacation_url, headers=header,verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    r = soup.find('div', {'id': 'allLocations'}).find_all('div', {'class': 'x-container'})

    for idx, val in enumerate(r):

        if idx != 0:
            if len(val.find_all('div', {'class': 'x-column'})) == 3:
                cb = val.find_all('div', {'class': 'x-column'})[1]

                locator_domain = base_url
                location_name = cb.find('h2', {'class': 'h-custom-headline'}).text.strip()
                bn = cb.find_all('p')[0].text.split('|')
                # print(len(bn) , cb.find_all('p')[0].text)
                if len(bn) == 2:
                    street_address = cb.find_all('p')[0].text.split('|')[0].strip()
                    phone = cb.find_all('p')[0].text.split('|')[1].strip()

                    vl = street_address.split(',')[0].replace('\n',' ').strip().split(' ')
                    vk = street_address.split(',')[-1].strip().split(' ')


                    state = vk[0].strip()
                    zip = vk[1].strip()

                    city = vl[-1]
                    vl.pop(-1)
                    street_address = ' '.join(vl)



                    hours_of_operation = ''
                    if len(cb.find_all('p')) == 2:
                        hours_of_operation = cb.find_all('p')[1].text.replace('\n','')

                    country_code = 'US'
                    store_number = '<MISSING>'
                    location_type = 'boombozz'
                    latitude = '<MISSING>'
                    longitude = '<MISSING>'

                    store = []
                    store.append(locator_domain if locator_domain else '<MISSING>')
                    store.append(location_name if location_name else '<MISSING>')
                    store.append(street_address if street_address else '<MISSING>')
                    store.append(city if city else '<MISSING>')
                    store.append(state if state else '<MISSING>')
                    store.append(zip if zip else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                    return_main_object.append(store)
                   # print("data === " + str(store))
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
