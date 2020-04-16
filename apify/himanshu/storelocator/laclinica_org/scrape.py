import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    locator_domain = base_url = "https://laclinica.org/"

    r = session.get("https://laclinica.org/wp-admin/admin-ajax.php?action=mapp_query&filters=&list=true&query%5Bpost_type%5D=location&debug=")
    json_data  = r.json()
    if 'pois' in json_data['data']:
        for key,value in enumerate(json_data['data']['pois']):
            location_name = value['title']
            street_address = '<MISSING>'
            city = '<MISSING>'
            state = '<MISSING>'
            zipp = '<MISSING>'
            # main_address = value['address'].split(',')
            r = session.get(value['url'])
            soup = BeautifulSoup(r.text, "lxml")

            main_address = soup.find('p', {'class': 'address'}).text.split(',')
            # print(main_address)

            if len(main_address) == 3:
                street_address = main_address[0].strip()
                city =  main_address[1].strip()
                state =  main_address[2].strip().split(' ')[0]
                zipp =  main_address[2].strip().split(' ')[1]
            elif len(main_address) == 4:
                street_address = main_address[0].strip() +''+ main_address[1].strip()
                city = main_address[2].strip()
                state = main_address[3].strip().split(' ')[0]
                zipp = main_address[3].strip().split(' ')[1]
            elif len(main_address) == 5:
                street_address = main_address[0].strip() + ' ' + main_address[1].strip() + ' ' + main_address[2].strip()
                city = main_address[3].strip()
                state = main_address[4].strip().split(' ')[0]
                zipp = main_address[4].strip().split(' ')[1]
            elif len(main_address) == 2:
                vk  = main_address[0].strip()
                street_address = vk
                city = '<MISSING>'
                if 'Oakland' in vk or 'Pittsburg' in vk:
                    city = vk.split(' ')[-1]
                    if 'Oakland' in vk.split(' '):
                        vk.split(' ').remove('Oakland')
                    elif 'Pittsburg' in vk.split(' '):
                        vk.split(' ').remove('Pittsburg')
                    street_address = vk
                
                state = main_address[1].strip().split(' ')[0]
                zipp = main_address[1].strip().split(' ')[1]

            latitude = value['point']['lat']
            longitude =  value['point']['lng']
            country_code = "US"
            store_number = '<MISSING>'
            phone = soup.find('p',{'class':'phone'}).text.replace('Phone:','').strip() if soup.find('p',{'class':'phone'}) else '<MISSING>'
            location_type = '<MISSING>'
            hours_of_operation = soup.find('p',{'class':'hours'}).text.replace('Hours:','').strip() if soup.find('p',{'class':'hours'}) else '<MISSING>'
            page_url = value['url']
            street_address  = street_address.lower().replace('suite','').replace('floor','').capitalize().replace(city,'')
            if "210 hospital drive vallejo" in street_address or "100 whitney ave vallejo" in  street_address:
                street_address = street_address.replace("vallejo",'')
                city = 'vallejo'
            if "2000 sierra road concord" in street_address:
                street_address = street_address.replace("concord",'')
                city = 'concord'
            store = [locator_domain, location_name, street_address.replace("oakland",''), city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip().replace('<br>','') if x else "<MISSING>" for x in store]

            yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
