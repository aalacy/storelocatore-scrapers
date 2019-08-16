import csv
import urllib2
import requests
import sgzip

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    for code in sgzip.for_radius(50):
        print('Pulling Zip Code %s...' % code)
        url = 'https://www.mykoolsmiles.com/api/locations/find_nearest'
        payload = {'zip': code,
                   'about_myself': 'other',
                   'page': 'https://www.mykoolsmiles.com/'
                   }
        r = session.post(url, headers=headers, data=payload)
        for line in r.iter_lines():
            if '"location_id":"' in line:
                items = line.split('"location_id":"')
                for item in items:
                    if '"brand_id":"' in item:
                        website = 'mykoolsmiles.com'
                        typ = 'Office'
                        name = item.split('"FacilityName":"')[1].split('"')[0]
                        add = item.split('"Address1":"')[1].split('"')[0]
                        city = item.split('"City":"')[1].split('"')[0]
                        state = item.split('"State":"')[1].split('"')[0]
                        zc = item.split('"ZIP":"')[1].split('"')[0]
                        phone = item.split('"OfficePhone":"')[1].split('"')[0].strip()
                        country = 'US'
                        store = item.split('"')[0]
                        hours = 'Mon: ' + item.split('Mon_Hours":"')[1].split('"')[0]
                        hours = hours + '; Tue: ' + item.split('Tue_Hours":"')[1].split('"')[0]
                        hours = hours + '; Wed: ' + item.split('Wed_Hours":"')[1].split('"')[0]
                        hours = hours + '; Thu: ' + item.split('Tue_Hours":"')[1].split('"')[0]
                        hours = hours + '; Fri: ' + item.split('Fri_Hours":"')[1].split('"')[0]
                        hours = hours + '; Sat: ' + item.split('Sat_Hours":"')[1].split('"')[0]
                        if 'Sun_Hours":""' not in item:
                            hours = hours + '; Sun: ' + item.split('Sun_Hours":"')[1].split('"')[0]
                        else:
                            hours = hours + '; Sun: Closed'
                        hours = hours.replace('; Sat: ;','; Sat: Closed;')
                        lat = item.split('"latitude":"')[1].split('"')[0]
                        lng = item.split('"longitude":"')[1].split('"')[0]
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
