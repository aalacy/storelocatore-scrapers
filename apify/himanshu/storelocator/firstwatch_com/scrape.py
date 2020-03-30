import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    return_main_object = []
    addresses = []
    coords = sgzip.coords_for_radius(50)


    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    locator_domain = "https://www.firstwatch.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    for cord in coords:
        try:
            r =session.get('https://www.firstwatch.com/api/get_locations.php?latitude='+str(cord[0])+'&longitude='+str(cord[1]),headers = headers)


            location_list = r.json()
        except:
            continue
        # print('https://www.firstwatch.com/api/get_locations.php?latitude='+str(cord[0])+'&longitude='+str(cord[1]))
        if location_list != []:

            for location in location_list:
                # print(location['zip'])
                # us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(location['zip']))[0]
                # ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(location['zip']))[0]
                # if location['zip'] not in[us_zip_list,ca_zip_list]:
                #     continue
                try:
                    location_name = location['name']
                    store_number = location['corporate_id']
                    if location['address_extended'] ==None :
                        street_address = location['address']
                    else:
                        street_address = location['address'] + " "+location['address_extended']
                    city = location['city']
                    state = location['state']
                    zipp = location['zip']
                    print(zipp)
                    latitude = location['latitude']
                    longitude = location['longitude']
                    phone = location['phone']
                    page_url = "https://www.firstwatch.com/locations/"+location['slug']

                    # if "OPEN NOW" not in location['open'] and 'open' not in location['open']  and "CLOSED" not in location['open']:

                    #     hours_of_operation = location['open'].replace('@','at')
                    #     # print(hours_of_operation)
                    #     # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    # else:
                    #     hours_of_operation = "<MISSING>"

                    hours = session.get(page_url,headers = headers)
                    soup = BeautifulSoup(hours.text,'lxml')
                    h_list = soup.find('script',{'id':'locations-detail'})
                    if h_list != None:
                        h1 = "Open Daily"+h_list.text.split('Open Daily')[-1].split('<br>')[0]
                        h2 = "Closed on"+h_list.text.split('Open Daily')[-1].split('<br>')[1].split('Closed on')[1].split('</p>')[0].replace('&amp;',"and")
                        hours_of_operation = h1 + " "+h2
                    else:
                        hours_of_operation = "<MISSING>"
                    # print(hours_of_operation)
                    # print('~~~~~~~~~~~~~~')
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                    store = ["<MISSING>" if x == "" or x == None else x for x in store]
                    if street_address in addresses:
                        continue
                    addresses.append(street_address)

                    #print("data = " + str(store))
                    #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                    return_main_object.append(store)
                except:
                    continue

    return return_main_object







def scrape():
    data = fetch_data()
    write_output(data)


scrape()
