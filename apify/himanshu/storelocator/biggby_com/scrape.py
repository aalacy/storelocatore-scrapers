import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
import phonenumbers
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('biggby_com')
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
    base_url = "https://www.biggby.com/"
    addresess = []

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    r = session.get("https://www.biggby.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    key = str(soup).split('"bgcSecurity":"')[1].split('","ajax":')[0]
    # print(key)
    data = soup.find_all("marker")
    for i in data:
        if i['coming-soon'] == "yes" :
            continue
        location_name = i['name']
        # print(location_name)
        street_address = i['address-one'] +" "+ i['address-two']
        city = i['city']
        state = i['state']
        zipp = i['zip']
        store_number = i['id']
        try:
            latitude = i['lat']
            longitude = i['lng']
        except KeyError:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        country_code = i['country']
        hours = ''
        if i['mon-thurs-open-hour']:
            try:
                mon_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                mon_open=mon_o.strftime("%I:%M %p")       
            except:
                mon_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                mon_open=mon_o.strftime("%I:%M %p")   
        else:
            mon_open = "close"

        if i['mon-thurs-close-hour']:
            try:
                mon_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                mon_close=mon_c.strftime("%I:%M %p")       
            except:
                mon_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                mon_close=mon_c.strftime("%I:%M %p")
        else:
            mon_close = "close"

        if i['fri-open-hour']:
            try:
                fir_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                fri_open=fir_o.strftime("%I:%M %p")       
            except:
                fir_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                fri_open=fir_o.strftime("%I:%M %p")
        else:
            fri_open = "close"

        if i['fri-close-hour']:
            try:
                fri_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                fri_close=fri_c.strftime("%I:%M %p")       
            except:
                mon_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                fri_close=fri_c.strftime("%I:%M %p")
        else:
            fri_close = "close"

        if i['sat-open-hour']:
            try:
                sat_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                sat_open=sat_o.strftime("%I:%M %p")       
            except:
                sat_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                sat_open=sat_o.strftime("%I:%M %p")
        else:
            sat_open = "close"

        if i['sat-close-hour']:
            try:
                sat_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                sat_close=sat_c.strftime("%I:%M %p")       
            except:
                sat_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                sat_close=sat_c.strftime("%I:%M %p")
        else:
            sat_close = "close"

        if i['sun-open-hour']:
            try:
                sun_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                sun_open=sun_o.strftime("%I:%M %p")       
            except:
                sun_o = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                sun_open=sun_o.strftime("%I:%M %p")
        else:
            sun_open = "close"

        if i['sun-close-hour']:
            try:
                sun_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H:%M")
                sun_close=sun_c.strftime("%I:%M %p")       
            except:
                sun_c = datetime.strptime(str(i['mon-thurs-open-hour']), "%H")
                sun_close=sun_c.strftime("%I:%M %p")
        else:
            sun_close = "close"
        hours = "mon thurs open hour"+"-"+str(mon_open)+" "+"mon thurs close hour"+"-"+str(mon_close)+" "+"fri open hour"+"-"+str(fri_open)+" "+"fri close hour"+"-"+str(fri_close)+" "+"sat open hour"+"-"+str(sat_open)+" "+"sat close hour"+"-"+str(sat_close)+" "+"sun open hour"+"-"+str(sun_open)+" "+"sun close hour"+"-"+str(sun_close)

        r1 = session.post("https://www.biggby.com/wp-admin/admin-ajax.php", headers=headers, data="action=biggby_get_location_data&security="+key+"&post_id="+str(i['pid'])).json()
        number = r1['phone-number'].replace("not available",'').replace("unavailable",'').replace("TBD","")
        if number:
            phone = phonenumbers.format_number(phonenumbers.parse(str(number), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        else:
            phone = "<MISSING>"
        store = []
        store.append(base_url)
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone)
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours if hours else '<MISSING>')
        store.append('<MISSING>')
        if store[2] in addresess:
            continue
        addresess.append(store[2])
        #logger.info("===", str(store))
        yield  store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()    
# (440) 385-7778
