import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://sweetoburrito.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('main')
    if exists:
        for data in soup.select('.flex_column.av_one_half'):
            location_name = data.select('.av-special-heading-tag')[0].get_text().strip()
            if "," in location_name:
                location_name = data.select('.av-special-heading-tag')[0].get_text().strip().split(',')[0].strip()
                city = location_name
                state = data.select('.av-special-heading-tag')[0].get_text().strip().split(',')[1].strip()
            else:
                if len(data.select('.av-special-heading-tag')[0].find_next('div').get_text()) < 2:
                    city = "<MISSING>"
                    state = "<MISSING>"
                else:
                    city_state = data.select('.av-special-heading-tag')[0].find_next('div').get_text().strip().split(',')
                    city = city_state[0].strip()
                    state = city_state[1].strip()
            if data.select('.iconbox_content_title'):
                phone = data.select('.iconbox_content_title')[0].get_text().strip()[7:]
            else:
                phone = "<MISSING>"
            zip = "<MISSING>"
            if "Hours" in data.select('.iconbox_content_container')[0].get_text().strip():
                address = data.select('.iconbox_content_container')[0].get_text().strip()[7:]
                hours_of_operation = address.split(":")[0][:-8]
                if "Address:" in data.select('.iconbox_content_container')[0].get_text().strip()[7:]:
                    addre = data.select('.iconbox_content_container')[0].get_text().strip()[7:].split('Address:')[1].split('for')[0].replace('Online', '').replace('Order', '').split(',')

                    street_address = addre[0].strip()
                    zip = "<MISSING>"
                else:
                    addre = data.select('.iconbox_content_container')[0].get_text().strip()[7:].replace('Online', '').replace('Order', '').split(',')[0].strip()
                    street_address = addre[0].strip()
                    zip = addre[1].strip() if len(addre[1].strip()) > 2 else "<MISSING>"
                phone = address.split(":")[3][4:-12]
            else:
                address = data.select('.iconbox_content_container')[0].get_text().strip()
                if "Address:" in data.select('.iconbox_content_container')[0].get_text().strip():
                    addres = data.select('.iconbox_content_container')[0].get_text().strip().split('Address:')[1].split('for')[0].replace('Online', '').replace('Order', '').strip().split(',')
                    if len(addres) == 2:
                        street_address = addres[0]
                        zip = addres[1].strip()
                    else:
                        street_address = addres[0]
                        zip = "<MISSING>"
                if "Sun" in address[:4] or "am" in address[:4] or "Mon-" in address[:4]:
                    if "Address" in address.split(":")[0]:
                        hours_of_operation = address.split(":")[0][:-8]
                    else:
                        hours_of_operation = address.split(":")[0]
                    if "AM" in address.split(":")[1][:4] or "pm" in address.split(":")[1][:4]:
                        hours_of_operation = hours_of_operation + " " + address.split(":")[1][:4]
                else:
                    address = data.select('.iconbox_content_container')[0].get_text().strip().split(",")
                    if "Fri" in address[0]:
                        add = address[0].split("83301")
                        hours_of_operation = add[1][:-12]
                    else:
                        hours_of_operation = "<MISSING>"
                    strt_address = data.select('.iconbox_content_container')[0].get_text().strip().replace('Online', '').replace('Order', '').strip()
                    if len(strt_address.split(',')) == 2:
                        street_address = strt_address.split(',')[0]
                        zip = strt_address.split(',')[1].strip().split(' ')[0] + " " + strt_address.split(',')[1].strip().split(' ')[1]
                        if len(strt_address.split(',')[1].strip().split(' ')) > 2:
                            hours_of_operation = ' '.join(strt_address.split(',')[1].strip().split(' ')[2:])
                    else:
                        if "Mon" in strt_address.split('Mon')[0].strip():
                            street_address = strt_address.split('Mon')[0].strip().split('Mon')[0]
                            hours_of_operation = "Mon" + strt_address.split('Mon')[0].strip().split('Mon')[1]
                        else:
                            street_address = strt_address.split('Mon')[0].strip()
                        zip = "<MISSING>"
            if ' ' in zip:
                zip = zip.strip().split(' ')[-1]
            if state in street_address:
                street_address =  street_address.split(state)[0]

            if zip in street_address:
                street_address = street_address.split(zip)[0]

            if 'Idaho' in street_address:
                street_address = street_address.split('Idaho')[0]

            id_id  = str(data.find('a')['href'].split('/')[-1].strip())
            lat = '<MISSING>'
            lng ='<MISSING>'
            db =  session.get('https://roxberry-api-ordering.crispnow.com/crispGetRestaurants?sid=ea543a90-1c79-4a6d-8179-fca50a481e60').json()

            for id,val in enumerate(db['restaurants']):
                bb = str(val['restaurantId'])
                if id_id in bb:


                    lat = val['restaurantLatitude']
                    lng = val['restaurantLongitude']

                # if id in x;

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours_of_operation)
            store.append(base_url)
            return_main_object.append(store)
        return return_main_object
    else:
        pass

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
