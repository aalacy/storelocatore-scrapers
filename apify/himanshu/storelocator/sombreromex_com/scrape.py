import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sombreromex_com')


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
    #     logger.info(link)

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
        try:
            url = script.find("h4").find("a")
            if url:
                if "https:" in url['href']:
                    page_url =  url['href']
                else:
                    page_url = base_url + url['href']
            else:
                page_url = "<MISSING>"
        except:
            page_url = "<MISSING>"

        list_store_data = list(script.stripped_strings)
        
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

            # logger.info(str(len(list_store_data)) + ' = list_store_data ===== ' + str(list_store_data))
            # logger.info('~~~~~~~~~~~~~~~~')
            if len(list_store_data) > 3:
                # logger.info(str(len(list_store_data)) + ' = list_store_data ===== ' + str(list_store_data))
                # logger.info(list_store_data[1].split(','))
                # logger.info('~~~~~~~~~~~~~~~~')
                location_name = list_store_data[0]
                phone = list_store_data[-2].replace(".","-")
                hours_of_operation = list_store_data[-1]
                # city = location_name

                if len(list_store_data[1].split(',')) > 1:
                    st_address = list_store_data[1].split(',')[0].split()
                    # logger.info(st_address)
                    # logger.info(len(st_address))
                    # logger.info(('~~~~~~~~~~~~~~~~`'))
                    if len(st_address) >4:
                        street_address = " ".join(st_address[:-2])
                        city = " ".join(st_address[-2:]).replace('Ave','').strip()
                        # logger.info(street_address +"/"+city)
                    else:
                        street_address = " ".join(st_address).strip()
                        city = " ".join(list_store_data[1].split(',')[1].split()[:2])

                    zipp = list_store_data[1].split(',')[1].split(' ')[-1]
                    state = list_store_data[1].split(',')[1].split(' ')[-2]
                    # logger.info(zipp,state)
                else:
                    street_address = " ".join(list_store_data[1].split()[:-4])
                    city =  " ".join(list_store_data[1].split()[-4:-2])
                    state = list_store_data[1].split()[-2]
                    zipp = list_store_data[1].split()[-1]


            else:
                # logger.info(str(len(list_store_data)) + ' = list_store_data ===== ' + str(list_store_data))
                # # logger.info(list_store_data[1].split(','))
                # logger.info('~~~~~~~~~~~~~~~~')
                hours_of_operation = list_store_data[-1]
                phone = list_store_data[-2].replace(".","-")

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
                    maps = location_soup.find("iframe")['src']
                    
                    latitude = maps.split("!3d")[1].split("!")[0]
                    longitude = maps.split("!2d")[1].split("!")[0]
            else:
                latitude = '<MISSING>'
                longitude = '<MISSING>'

            if not phone.replace('-', '').isdigit():
                phone = '<MISSING>'


            store = [locator_domain, location_name, street_address.replace("5550 Lake Murray Blvd","1550 Lake Murray Blvd").replace("1535 E. Ontario","1535 E. Ontario Avenue"), city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
