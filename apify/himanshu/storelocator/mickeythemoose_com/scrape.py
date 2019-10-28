import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import platform
system = platform.system()

def get_driver():
   options = Options()
   options.add_argument('--headless')
   options.add_argument('--no-sandbox')
   options.add_argument('--disable-dev-shm-usage')
   options.add_argument('--window-size=1920,1080')
   if "linux" in system.lower():
       return webdriver.Firefox(executable_path='./geckodriver', options=options)
   else:
       return webdriver.Firefox(executable_path='geckodriver.exe', options=options)
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    driver = get_driver()

    base_url = "https://mickeythemoose.com"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "content-type":'application/x-www-form-urlencoded; charset=UTF-8',
        "origin": "https://mickeythemoose.com",
        "x-requested-with": "XMLHttpRequest",
        "x-wp-nonce": "0f3f23cdf8",
        "x-wpgmza-action-nonce": "24a3c3c318"
   }
    # r = requests.post("https://mickeythemoose.com/wp-json/wpgmza/v1/marker-listing/",headers=headers,data='phpClass=WPGMZA%5CMarkerListing%5CBasicTable&start=0&length=10000&map_id=1').json()
    r = requests.post("https://mickeythemoose.com/store-locator/")
    driver.get("https://mickeythemoose.com/store-locator/")

    temp_soup = BeautifulSoup(driver.page_source, "lxml")

    # soup = BeautifulSoup(r.text,"lxml")
    for id,val in enumerate(temp_soup.find_all('script')):
        if id  == 76:

            json_data = json.loads(val.text.split('var wpgmaps_localize_marker_data =')[1].split(';')[0])

            i = 0
            for val in json_data:
                for x  in json_data[val]:
                    value  = json_data[val][x]

                    name = 'Mickey Mart ' + value['title'].strip()


                    addr = value['address'].strip()
                    ck = addr.split(',')[0].split(' ')

                    ck.pop(-1)
                    address = ' '.join(ck).strip()
                    # city = addr.split(',')[0].split(' ')[-1]
                    state = ''
                    zip = ''

                    if len(addr.strip().split(',')) ==2:
                        if len(addr.split(',')[1].strip().split(' ')) == 2:
                            state = addr.split(',')[1].strip().split(' ')[0]
                            zip = addr.split(',')[1].strip().split(' ')[1]
                    if len(addr.strip().split(',')) == 3:
                        if len(addr.split(',')[2].strip().split(' ')) == 3:
                            state = addr.split(',')[2].strip().split(' ')[0]
                            zip = addr.split(',')[2].strip().split(' ')[1]
                    country = 'US'
                    storeno = ''
                    r  =  requests.get(value['linkd'])
                    city = value['linkd'].split('/')[-1].split('-',2)[-1]
                    # exit()
                    soup =  BeautifulSoup(r.text,"lxml")



                    phone = soup.find('p',{'id':'address'}).find_next('p').text
                    if '(' not in phone:
                        phone = ''
                    lat = value['lat']
                    lng = value['lng']
                    hour = soup.find('p',{'id':'address'}).find_next('ul').text.replace('\n',' ').replace('\r',' ')
                    page_url = 'https://mickeythemoose.com/store-locator/'
                    # name = soup.find('h1',{'class':'entry-title'}).text

                    store=[]
                    store.append(base_url)
                    store.append(name if name else "<MISSING>")
                    store.append(address if address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zip if zip else "<MISSING>")
                    store.append(country if country else "<MISSING>")
                    store.append(storeno if storeno else "<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour if hour else "<MISSING>")
                    store.append(page_url if hour else "<MISSING>")

                    print("data ==== "+str(store))
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
