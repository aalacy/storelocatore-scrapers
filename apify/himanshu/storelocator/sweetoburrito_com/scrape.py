import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sweetoburrito_com')


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
    db =  session.get('https://roxberry-api-ordering.crispnow.com/crispGetRestaurants?sid=ea543a90-1c79-4a6d-8179-fca50a481e60').json()
    for val in (db['restaurants']):
        hours_of_operation = ''
        store_number = str(val['restaurantId'])
        zipp = val['restaurantZipCode']
        if "1111" in store_number:
            continue
        if "99207" in zipp:
            hours_of_operation = "11AM to 9PM Mon-Thu, 11AM to 10PM Fri-Sat, 11AM to 7PM Sun"
        if "99218" in zipp:
            hours_of_operation = "11AM to 8PM Mon-Sat, 11AM to 7PM Sun"
        lat = val['restaurantLatitude']
        lng = val['restaurantLongitude']
        location_name = val['restaurantName']
        location_type = "<MISSING>"
        if "83814" in zipp or "99037" in zipp:
            hours_of_operation = "11AM to 9PM Mon-Sat, 11AM to 7PM Sun"
        if "84341" in zipp or "84020" in zipp:
            hours_of_operation = "Mon-Thurs 11AM-9PM Fri-Sat 11AM-10PM"
        if "84020" in zipp:
            hours_of_operation = hours_of_operation +" Sun 11AM-8PM"
        country_code = val['restaurantCountryName']
        phone = val['restaurantPhone']
        if "83404" in zipp:
            hours_of_operation = "Sun-thurs 10:30AM – 10:00PM Friday and Saturday 10:30-11PM"
        page_url = "https://sweetoburrito-orders.crispnow.com/locations/"+str(store_number)
        locator_domain = "https://sweetoburrito.com/"
        if "22556" in zipp:
            hours_of_operation = "Friday and Saturday 11am-10pm Sunday through Thursday 11am-9pm" 
        street_address = val['restaurantAddress']
        city = val['restaurantCity']
        if "83301" in zipp:
            hours_of_operation = "Mon to Thur 7:30am to 9pm Fri and Sat 7:30am to 10pm Sun 8am to 9pm"
        state = val['restaurantStateName']
        if "84087" in zipp:
            hours_of_operation = "Mon-thurs 11AM-10PM Friday-Sat 11AM-11PM Closed Sunday"
        store = []
        store.append(locator_domain)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours_of_operation)
        store.append(page_url)
        yield store
    base_url = "https://sweetoburrito.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    exists = soup.find('main')
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
            phone = "mp"
        else:
            address = data.select('.iconbox_content_container')[0].get_text().strip()
            if "Address:" in data.select('.iconbox_content_container')[0].get_text().strip():
                addres = data.select('.iconbox_content_container')[0].get_text().strip().split('Address:')[1].split('for')[0].replace('Online', '').replace('Order', '').strip().split(',')
                if len(addres) == 2:
                    street_address = addres[0].replace(" Provo","").replace(" Orem","")
                    # logger.info(street_address)
                    zip = addres[1].strip()
                else:
                    street_address = addres[0]
                   # logger.info(street_address)
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
        if "84057" in zip:
            hours_of_operation = hours_of_operation +" Friday and Saturday Closed Sunday"
        store = []
        store.append("https://sweetoburrito.com/")
        store.append(location_name)
        store.append(street_address.replace("Woodbridge","").replace("703-763-3516","").replace("Suite G Riverdale","Suite G").strip())
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.replace("<MISSING>","703-763-3516"))
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation.replace(" (drive thru open til 11)",""))
        store.append(base_url)
        if "Spokane" in city or "Idaho Falls" in city or "Coeur D’ Alene" in city or "Woods Cross" in city or "Draper" in city or "Stafford" in city or "Logan" in city:
            continue
        if "Twin Falls" in location_name :
            continue
        store = [x.strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
