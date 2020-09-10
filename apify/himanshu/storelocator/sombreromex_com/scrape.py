import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    base_url = "https://www.sombreromex.com"
    r = session.get("https://www.sombreromex.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    for script in soup.find_all('div', {'class': 'mmtl-col mmtl-col-sm-3'}):
        
        list_store_data = list(script.stripped_strings)
        if script.find(lambda tag: (tag.name == "a") and "More Info" in tag.text) is not None:
            url = script.find(lambda tag: (tag.name == "a") and "More Info" in tag.text)['href']
            if "https:" in url:
                page_url =  url
            else:
                page_url = base_url + url
        else:
            page_url = "<MISSING>"
        
        if len(list_store_data) > 1:

            if 'Order Food Delivery with DoorDash' in list_store_data:
                list_store_data.remove('Order Food Delivery with DoorDash')

            if 'Coming Soon!' in list_store_data:
                list_store_data.remove('Coming Soon!')

            if 'More Info' in list_store_data:
                list_store_data.remove('More Info')

            if 'Drive Thru' in list_store_data:
                list_store_data.remove('Drive Thru')

            if 'Download Menu' in list_store_data:
                list_store_data.remove('Download Menu')

            if 'Location Hours' in list_store_data:
                list_store_data.remove('Location Hours')

            if 'Visit or call for menu info.' in list_store_data:
                list_store_data.remove('Visit or call for menu info.')

            if 'Order Online' in list_store_data:
                list_store_data.remove('Order Online')
            if 'Online Ordering Coming Soon, Please Call Location for Takeout' in list_store_data:
                list_store_data.remove("Online Ordering Coming Soon, Please Call Location for Takeout")

            # print(str(len(list_store_data)) + ' = list_store_data ===== ' + str(list_store_data))
            # print('~~~~~~~~~~~~~~~~')

            if len(list_store_data) > 3:
                # print(str(len(list_store_data)) + ' = list_store_data ===== ' + str(list_store_data))
                # print(list_store_data[1].split(','))
                # print('~~~~~~~~~~~~~~~~')
                location_name = list_store_data[0]
                phone = list_store_data[-2]
                hours_of_operation = list_store_data[-1]
                # city = location_name

                if len(list_store_data[1].split(',')) > 1:
                    st_address = list_store_data[1].split(',')[0].split()
                    # print(st_address)
                    # print(len(st_address))
                    # print(('~~~~~~~~~~~~~~~~`'))
                    if len(st_address) >4:
                        street_address = " ".join(st_address[:-2])
                        city = " ".join(st_address[-2:]).replace('Ave','').strip()
                        # print(street_address +"/"+city)
                    else:
                        street_address = " ".join(st_address).strip()
                        city = " ".join(list_store_data[1].split(',')[1].split()[:2])

                    zipp = list_store_data[1].split(',')[1].split(' ')[-1]
                    state = list_store_data[1].split(',')[1].split(' ')[-2]
                    # print(zipp,state)
                else:
                    street_address = " ".join(list_store_data[1].split()[:-4])
                    city =  " ".join(list_store_data[1].split()[-4:-2])
                    state = list_store_data[1].split()[-2]
                    zipp = list_store_data[1].split()[-1]


            else:
                # print(str(len(list_store_data)) + ' = list_store_data ===== ' + str(list_store_data))
                # # print(list_store_data[1].split(','))
                # print('~~~~~~~~~~~~~~~~')
                hours_of_operation = list_store_data[-1]
                phone = list_store_data[-2]

                zipp = list_store_data[0].split(',')[-1].split(' ')[-1]
                state = list_store_data[0].split(',')[-1].split(' ')[-2]

                if len(list_store_data[0].split(',')) > 1:
                    street_address =  " ".join(list_store_data[0].split(',')[0].split()[:-1])
                    city =  "".join(list_store_data[0].split(',')[0].split()[-1])
                else:
                    street_address = ' '.join(list_store_data[0].split(',')[0].split(' ')[:-3])
                    city = ''.join(list_store_data[0].split(',')[0].split(' ')[-3])

                location_name = street_address.split(' ')[-1]
        

            country_code = 'US'
            store_number = '<MISSING>'
            if page_url != "<MISSING>":
                location_soup = BeautifulSoup(session.get(page_url, headers=headers).text, "lxml")
                maps = location_soup.find("a",text=re.compile("Get Directions"))
                if "@" in maps['href']:
                    latitude = maps['href'].split("@")[1].split(",")[0]
                    longitude = maps['href'].split("@")[1].split(",")[1]
                else:
                    latitude = '<MISSING>'
                    longitude = '<MISSING>'


            else:
                latitude = '<MISSING>'
                longitude = '<MISSING>'

            if not phone.replace('-', '').isdigit():
                phone = '<MISSING>'


            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
