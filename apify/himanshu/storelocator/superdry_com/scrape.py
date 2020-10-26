import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
import unicodedata


session = SgRequests()

def hour_split(s, chunk_size):
    a = zip(*[s[i::chunk_size] for i in range(chunk_size)])
    return [''.join(t) for t in a]


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    zips = sgzip.coords_for_radius(100)
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "https://www.superdry.com/"
    locator_domain = "https://www.superdry.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    for zip_code in zips:
        # print(zip_code)


        r = session.get('https://www.superdry.com/index.php?option=com_store_collect&lng='+str(zip_code[1])+'&lat='+str(zip_code[0])+'&format=raw&task=nearest',headers = headers)

        try:
            json_data = r.json()
        except:

            continue


        if json_data != []:
            for  z in json_data:

                location_name = z['name']
                street_address = z['address']
                if len(z['city'].split(',')) >1:
                    city = z['city'].split(',')[0]
                    state = z['city'].split(',')[-1]
                else:
                    city = z['city'].split(',')[0]
                    if re.findall("[a-zA-Z]+", z['postcode']) != []:
                        state = "".join(re.findall("[a-zA-Z]+", z['postcode']))
                        # print(state)
                    else:
                        state = "<MISSING>"

                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),z['postcode'])
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',z['postcode'])
                if us_zip_list :
                    zipp = us_zip_list[0]
                    country_code = "US"
                elif ca_zip_list:
                    zipp = ca_zip_list[0]
                    country_code = "CA"
                else:
                    continue
                # print(zipp)

                phone = z['phone']
                latitude = z['latitude']
                longitude = z['longitude']
                if "-" in str(latitude):
                    latitude,longitude = longitude,latitude
                hours = z['openingHours']
                h = []
                for i in hours:
                    h1 = ".".join(hour_split(i['hours'].split('-')[0],2))

                    h2= ".".join(hour_split(i['hours'].split('-')[-1].replace('\r','').strip(),2))
                    h_format = h1+" AM - " + h2 + " PM"
                    # print(h_format)
                    if "CL.OS.ED" not in h_format:
                        hours1 = i['day']+" " + h_format
                        # print(hours1)
                        h.append(hours1)
                    else:
                        hours1 = i['day']+" " + i['hours']
                        # print(hours1)
                        h.append(hours1)
                hours_of_operation = ",".join(h).replace('\r','').strip()
                page_url = "<MISSING>"




                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')

                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                if store[2] in addresses:
                    continue

                addresses.append(store[2])
                # print("data===="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                yield store




def scrape():
    data = fetch_data()
    write_output(data)
scrape()
