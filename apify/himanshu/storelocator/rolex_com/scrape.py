import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def hasNumbers(inputString):
     return any(char.isdigit() for char in inputString)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    return_main_object = []
    base_url = "https://www.rolex.com/"

    addresses= []


    r = requests.get("https://retailers.rolex.com/app/establishments/light/jsFront?establishmentType=STORE&langCode=en&brand=RLX&countryCodeGeofencing=US").json()

    for vj in r:
        try:

            locator_domain = base_url
            location_name = vj['nameTranslated'].encode('ascii', 'ignore').decode('ascii').strip().replace('<br/>','')
            street_address = vj['streetAddress'].encode('ascii', 'ignore').decode('ascii').strip().replace('<br/>','')

            b = vj['address'].split('<br/>')
            if(b[-1] == 'United States' or b[-1] == 'Canada'):
                if len(b) == 5:

                    del b[0]

                    if b[-1] == 'United Kingdom':
                        country_code = 'US'
                    if b[-1] == 'Canada':
                        country_code = 'CA'
                    city = b[0].encode('ascii', 'ignore').decode('ascii').strip()


                    state = b[1].encode('ascii', 'ignore').decode('ascii').strip()

                    # print(state)
                    if hasNumbers(city):
                        city = ''

                    # break


                elif len(b) == 4:


                    if b[-1] == 'United Kingdom':
                        country_code = 'US'
                    if b[-1] == 'Canada':
                        country_code = 'CA'

                    city = '<INACCESSIBLE>'

                    state = b[1].split(' ')
                    # print(b)
                    # print(state)
                    # print(len(state))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    if len(b[1].split(' ')) <4:
                        state =b[1].split(' ')[-1]
                    else:
                        state = " ".join(b[1].split(' ')[-2:]).replace('City','').strip()



                    if hasNumbers(city):
                        city = ''

                elif len(b) == 6:



                    if b[-1] == 'United Kingdom':
                        country_code = 'US'
                    if b[-1] == 'Canada':
                        country_code = 'CA'
                    city = b[-4].encode('ascii', 'ignore').decode('ascii').strip()
                    if hasNumbers(city):
                        city = ''
                    state = b[-2].encode('ascii', 'ignore').decode('ascii').strip()


                zip = vj['postalCode'].encode('ascii', 'ignore').decode('ascii').strip()

                store_number = vj['dealerId']
                phone = vj['phone1'].encode('ascii', 'ignore').decode('ascii').strip()
                location_type = ''
                latitude = vj['lat']
                longitude = vj['lng']

                if street_address in addresses:
                    continue
                addresses.append(street_address)
                k = requests.get('https://www.rolex.com/rolex-dealers/dealer-locator/retailers-details/' + str(vj['urlRolex']))

                soup1 = BeautifulSoup(k.text, "lxml")

                hours_of_operation = ''
                page_url = 'https://www.rolex.com/rolex-dealers/dealer-locator/retailers-details/' + str(vj['urlRolex'])

                if soup1.find('span',{'itemprop':'openingHours'}) != None:
                    hours_of_operation = soup1.find('span',{'itemprop':'openingHours'}).text.encode('ascii', 'ignore').decode('ascii').strip()

                if ' ' in state:

                    state = state.split(' ')[-1]
                else:
                    state = state
                if hasNumbers(state):
                    if len(b) >4:
                        state = b[-3].strip()
                    else:
                        state = b[-2].strip()



                if "Columbia" in  state:
                    state = "British Columbia"
                if "Beach Florida" in state:
                    state = "Florida"
                if "Carolina" == state or "Jersey" == state or "York" == state or "Island" == state or "Hampshire" == state or  "Mexico" == state:
                        state = " ".join(b[1].split(' ')[-2:]).replace('City','').strip()
                if "Edmonton Alberta" in state:
                    state = "Alberta"

                # print(state)


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
                store.append(page_url if page_url else '<MISSING>')
                # if store_number in address:
                #     continue
                # addresses.append(store_number)
                # print("data====",str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
                return_main_object.append(store)
                # yield store

        except:
            continue


    return return_main_object



def scrape():
    data = fetch_data()

    write_output(data)


scrape()
