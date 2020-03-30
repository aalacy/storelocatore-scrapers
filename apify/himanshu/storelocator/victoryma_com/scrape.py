import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://victoryma.com/"
    r = session.get(base_url, headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find_all('script')[-1]
    # print(script)
    script_text = script.text.split('var sites = ')[-2].split(';')[0].split('\n')
    script_text = [x for x in script_text if x.strip()]

    del script_text[0]
    del script_text[-1]
    c =[]
    for i in script_text :
        list_i = i.replace('    [','').split('],')

        lat= list_i[0].split(',')[2].replace("'",'')
        lon = list_i[0].split(',')[3].replace("'",'')
        c.append(lat)
        c.append(lon)





    for val in soup.find('li', {'class': 'about-school-menu'}).find('ul', {'class': 'program-sub-nav'}).find_all('a'):



        # print(coord)
        r = session.get(base_url + val['href'], headers=header)
        soup = BeautifulSoup(r.text, "lxml")
        locator_domain = base_url
        location_name = soup.find('div', {'class': 'school-address'}).find('h2').text.strip()
        address = soup.find('span', {'class': 'address'}).text.strip()
        address = re.sub("\s\s+", " ", address).split(',')

        if len(address) ==4:
            street_address = " ".join(address[:2])
        else:
            street_address = address[0].strip()
        # print(city,state,street_address,)
        city = soup.find('span', {'class': 'address'}).text.strip().split(',')[-2].strip()
        st = soup.find('span', {'class': 'address'}).text.strip().split(',')[-1].strip().split(' ')[0].replace('\t','')
        if "Spain".lower() == st.lower():
            state = "<MISSING>"
        else:
            state = st
        # print(state)

        zip = soup.find('span', {'class': 'address'}).text.strip().split(',')[-1].strip().split(' ')[1].replace('\t','')
        store_number = '<MISSING>'
        phone = soup.find('span',{'class':'no'}).text
        country_code = 'US'
        location_type = '<MISSING>'

        page_url = base_url + val['href']
        hour = soup.find('ul',{'class':'working-hours'}).find_all('a')
        db = []
        for i in hour:

            db.append(i.text.strip().replace(" ", ""))

        hours_of_operation = ' '.join(db).replace('\n',' ').replace('\t','')
        latitude = c.pop(0)
        longitude= c.pop(0)
        # print(latitude,longitude)



        store=[]
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


        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        # print("data == "+str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
