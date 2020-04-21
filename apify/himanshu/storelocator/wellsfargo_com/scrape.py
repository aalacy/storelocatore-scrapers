import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
# import time

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    # coord = search.next_coord()
    current_results_len = 0 
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        locator_domain = ''
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        page_url = ""
        hours_of_operation = ""

        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        #print("zip_code === "+zip_code)
        # x = coord[0]
        # y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        try:
            r = session.get('https://www.wellsfargo.com/locator/search/?searchTxt='+str(zip_code)+'&mlflg=N&sgindex=99&chflg=N&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on')
                                
        except:
            continue
        soup = BeautifulSoup(r.text, 'lxml')
        result = soup.find('div',{'id':'resultsSide'})
        if result != None:
            current_results_len = len(result.find_all('li',class_='aResult'))
            for li in result.find_all('li',class_='aResult'):
                #print(li)
                try:
                    left_data = li.find('div',class_='vcard')
                    adr = left_data.find('address',class_='adr')
                    locator_domain= "https://www.wellsfargo.com/"
                    location_type = left_data.find('div',class_='fn heading').text.split('|')[0].strip().replace('+','and').strip()
                    location_name = adr.find('div',{'itemprop':'addressLocality'}).text.strip().capitalize()
                    street_address = adr.find('div',class_='street-address').text.strip().capitalize()
                    city= adr.find('span',class_='locality').text.strip().capitalize()
                    state = adr.find('abbr',class_='region').text.strip()
                    zipp_tag = adr.find('span',class_='postal-code').text.strip()
                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_tag))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_tag))
                    if ca_zip_list:
                        zipp = ca_zip_list[-1]
                        country_code = "CA"
                    if us_zip_list:
                        zipp = us_zip_list[-1]
                        country_code = "US"
                    phone_tag = left_data.find('div',class_='tel').text.replace('Phone:','').strip()
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                    if phone_list != []:
                        phone = phone_list[0].strip()
                    else:
                        phone="<MISSING>"
                    hours = li.find('div',class_='rightSideData')
                    list_hours= list(hours.stripped_strings)
                    if "Outage Alert" in list_hours:
                        list_hours.remove('Outage Alert')
                    if "Unavailable:" in list_hours :
                        list_hours.remove('Unavailable:')
                    if "ATMs" ==  list_hours[2]:
                        list_hours.remove('ATMs')
                        # print(list_hours)
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    if list_hours == []:
                        hours_of_operation = "<MISSING>"
                    elif "Features" in list_hours[0]:
                        hours_of_operation = 'ATMs'+' '.join(list_hours).split('ATMs')[1].replace('&','and').strip()
                    else:
                        hours_of_operation = " ".join(list_hours).strip().replace('&','and').strip()
                    page_url = 'https://www.wellsfargo.com/locator/search/?searchTxt='+str(zip_code)+'&mlflg=N&sgindex=99&chflg=N&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on'
                except:
                    pass
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [x if x else "<MISSING>" for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                #print("data = " + str(store))
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                # return_main_object.append(store)
                yield store
        
        
                
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
    
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
