import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://shop.guess.com/en/storelocator//"
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }



    location_url = "https://stores.guess.com.prod.rioseo.com/"
    r = session.get(location_url,headers=headers)

    soup = BeautifulSoup(r.text,"lxml")

    for i in soup.find('ul',{'class':'custom-map-list'}).find_all('a'):

        r1 = session.get(i['href'], headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        for j in soup1.find('ul',{'class':'custom-map-list'}).find_all('a'):
            r2 = session.get(j['href'], headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            for k in soup2.find('ul', {'class': 'custom-map-list'}).find_all('li'):
                r3 = session.get(k.find('a')['href'], headers=headers)
                soup3 = BeautifulSoup(r3.text, "lxml")
                if soup3.find('div',{'class':'location-name-wrap'}) !=None:
                    location_name =  soup3.find('span',{'class':'location-name capitalize underline'}).text
                    phone = soup3.find('a',{'class':'phone'}).text.strip()
                    latitude = soup3.find('a',{'class':'directions'})['href'].split(',')[-2].split('=')[-1]
                    longitude = soup3.find('a',{'class':'directions'})['href'].split(',')[-1]
                    hours_of_operation = re.sub(r"\s+", " ", soup3.find('div',{'class':'hours'}).text)
                    page_url =  k.find('a')['href']

                    if len(list(soup3.find("p",{"class":"address"}).stripped_strings)) == 3:
                    
                        street_address = ' '.join(list(soup3.find("p",{"class":"address"}).stripped_strings)[0:2])
                        city = list(soup3.find("p",{"class":"address"}).stripped_strings)[-1].split(',')[0]
                        state = list(soup3.find("p",{"class":"address"}).stripped_strings)[-1].split(',')[1].split(' ')[1]
                        zip = list(soup3.find("p",{"class":"address"}).stripped_strings)[-1].split(',')[1].split(' ')[2]
                    else:
                        street_address = ''.join(list(soup3.find("p",{"class":"address"}).stripped_strings)[0])
                        city = list(soup3.find("p",{"class":"address"}).stripped_strings)[-1].split(',')[0]
                        state = list(soup3.find("p",{"class":"address"}).stripped_strings)[-1].split(',')[1].split(' ')[1]
                        zip = list(soup3.find("p",{"class":"address"}).stripped_strings)[-1].split(',')[1].split(' ')[2]

                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zip))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zip))

                    if ca_zip_list:
                        zip = ca_zip_list[-1]
                        country_code = "CA"
                    if us_zip_list:
                        zip = us_zip_list[-1]
                        country_code = "US"


                else:
                    location_name = soup2.find("span",{"class":"location-name uppercase"}).text
                    street_address =  list(soup2.find("div",{"class":"address"}).stripped_strings)[0]
                    city = list(soup2.find("div",{"class":"address"}).stripped_strings)[1].split(',')[0]
                    state = list(soup2.find("div",{"class":"address"}).stripped_strings)[1].split(',')[1].split(' ')[1]
                    zip = list(soup2.find("div",{"class":"address"}).stripped_strings)[1].split(',')[1].split(' ')[2]
                    phone = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    page_url = j['href']
                  
                    latitude = soup2.find("div",{"class":"map-list-item-link flex space-between mt-10"}).find('a')['href'].split(',')[-2].split('=')[-1]
                    longitude = soup2.find("div",{"class":"map-list-item-link flex space-between mt-10"}).find('a')['href'].split(',')[-1]
                
                locator_domain = base_url
                store_number = ''
               
                location_type = '<MISSING>'
               
                if street_address in addresses:
                    continue

                addresses.append(street_address)

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
                # print("===", str(store))
                # return_main_object.append(store)
                yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
