import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    return_main_object = []
    base_url = "https://www.rolex.com/"

    addresses = []

    r = session.get(
        "https://retailers.rolex.com/app/establishments/light/jsFront?establishmentType=STORE&langCode=en&brand=RLX&countryCodeGeofencing=US").json()

    for vj in r:
        try:
            locator_domain = base_url
            location_name = vj['nameTranslated'].encode(
                'ascii', 'ignore').decode('ascii').strip().replace('<br/>', ' ')
            street_address = vj['streetAddress'].encode(
                'ascii', 'ignore').decode('ascii').strip().replace('<br/>', ' ')

            b = vj['address'].split('<br/>')

            if(b[-1] == 'United States' or b[-1] == 'Canada'):
                if hasNumbers((str(b[-3]))):
                    state = b[-2].strip()
                    city = b[-4].strip()
                else:
                    if len(b[-3].split()) == 1:
                        state = b[-3].strip()
                        city = b[-4].strip()

                    elif len(b[-3].split()) == 2:
                        city = b[-3].split()[0].strip()
                        state = b[-3].split()[-1].strip()
                    elif len(b[-3].split()) == 3:
                        # print(b[-3].split())
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        city = " ".join(
                            b[-3].split()[:-1]).replace('North', '').replace('South', '')
                        if "New" == city.split()[-1]:
                            city = city.replace('New', '')
                        state = "".join(b[-3].split()[-1])
                        if "Jersey" == state or "York" == state:
                            state = " ".join(b[-3].split()[1:])

                        if "South" == b[-3].split()[1] or "North" == b[-3].split()[1]:
                            state = " ".join(b[-3].split()[1:]).strip()
                    elif len(b[-3].split()) == 4:
                        if "City" == b[-3].split()[-2] or "Prussia" == b[-3].split()[-2] or "Beach" == b[-3].split()[-2] or "Gardens" == b[-3].split()[-2] or "Moines" == b[-3].split()[-2] or "Estate" == b[-3].split()[-2]:
                            city = " ".join(b[-3].split()[:-1]).strip()
                            state = b[-3].split()[-1].strip()
                        else:
                            city = " ".join(b[-3].split()[:-2]).strip()
                            state = " ".join(b[-3].split()[-2:]).strip()
                    else:
                        city = " ".join(b[-3].split()[:2]).strip()
                        state = "".join(b[-3].split()[-1]).strip()
                if "Columbia" == state:
                    # state = " ".join(b[-3].split(',')[1:])
                    state = "British Columbia"
                    # print(state)
                if "Mexico" == state or "Hampshire" == state or "Island" == state:
                    state = " ".join(b[-3].split()[1:])
                    # print(state)
                if b[-1] == 'United States':
                    country_code = "US"
                elif b[-1] == 'Canada':
                    country_code = "CA"
                else:
                    pass
                    # print(b[-1])
                    # print("~~~~~~~~~~~~~")
                zip = vj['postalCode'].encode(
                    'ascii', 'ignore').decode('ascii').strip()
                # print(city + " | " + state + " | " +
                #       zip + " |  " + country_code)

                phone = vj['phone1'].encode(
                    'ascii', 'ignore').decode('ascii').strip()
                store_number = vj['dealerId']
                location_type = ''
                latitude = vj['lat']
                longitude = vj['lng']
                k = session.get(
                    'https://www.rolex.com/rolex-dealers/dealer-locator/retailers-details/' + str(vj['urlRolex']))

                soup1 = BeautifulSoup(k.text, "lxml")

                hours_of_operation = ''
                page_url = 'https://www.rolex.com/rolex-dealers/dealer-locator/retailers-details/' + \
                           str(vj['urlRolex'])

                if soup1.find('span', {'itemprop': 'openingHours'}) != None:
                    hours_of_operation = soup1.find('span', {'itemprop': 'openingHours'}).text.encode(
                        'ascii', 'ignore').decode('ascii').strip()
                else:
                    hours_of_operation = "<MISSING>"

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append('<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')

                store.append(
                    hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # print(zip)
                #print("data====", str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
                return_main_object.append(store)
                # yield store

        except:
            continue

    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
