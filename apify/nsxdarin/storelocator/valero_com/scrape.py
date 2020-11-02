import csv
import urllib.request, urllib.error, urllib.parse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

driver = get_driver()

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def parse_address(raw_address):
    try:
        return parse_address_with_usaddress(raw_address)
    except:
        return parse_address_with_heuristics(raw_address)

def parse_address_with_usaddress(raw_address):
    parsed = usaddress.tag(raw_address)[0]
    city = parsed['PlaceName']
    address = raw_address.rsplit(city, 1)[0].strip()
    return { "city": city, "address": address }

def parse_address_with_heuristics(raw_address):
    try:
        without_zip_and_state = raw_address.rsplit(',', 1)[0].strip()
        city = without_zip_and_state.rsplit(' ', 1)[1].strip()
        address = without_zip_and_state.rsplit(' ', 1)[0].strip()
        return { "city": city, "address": address }
    except:
        return { "city": "<INACCESSIBLE", "state": "<INACCESSIBLE>" }

def fetch_data():
    keys = set()
    url = 'https://valeromaps.valero.com/Home/Search?SPHostUrl=https%3A%2F%2Fwww.valero.com%2Fen-us'
    driver.get('https://www.valero.com/en-us/ProductsAndServices/Consumers/StoreLocator')
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    for x in range(15, 50, 5):
        for y in range(-65, -120, -5):
            nelat = float(x) + 5
            swlat = float(x) - 5
            nelng = float(y) + 5
            swlng = float(y) - 5
            payload = {'NEBound_Lat': str(nelat),
                       'NEBound_Long': str(nelng),
                       'SWBound_Lat': str(swlat),
                       'SWBound_Long': str(swlng),
                       'center_Lat': x,
                       'center_Long': y
                       }
            r = session.post(url, headers=headers, data=payload)
            if r.encoding is None: r.encoding = 'utf-8'
            for line in r.iter_lines(decode_unicode=True):
                if 'UniqueID":"' in line:
                    items = line.split('UniqueID":"')
                    for item in items:
                        if '"DetailName":"' in item:
                            name = item.split('"StationName":"')[1].split('"')[0]
                            phone = item.split('Phone":"')[1].split('"')[0].strip().replace('\t','')
                            lat = item.split('Latitude":')[1].split(',')[0]
                            lng = item.split(',"Longitude":')[1].split(',')[0]
                            store = item.split('"')[0]
                            website = 'valero.com'
                            loc = '<MISSING>'
                            typ = '<MISSING>'
                            addinfo = item.split('"Address":"')[1].split('"')[0]
                            zc = addinfo.rsplit(' ',1)[1]
                            state = addinfo.split(',')[-1].strip().split(' ')[0]
                            parsed = parse_address(addinfo)
                            city = parsed["city"] if parsed["city"].strip() else "<INACCESSIBLE>"
                            address = parsed["address"] if parsed["address"].strip() else "<INACCESSIBLE>"
                            hours = '<MISSING>'
                            country = 'US'
                            if phone == '':
                                phone = '<MISSING>'
                            key = name + '|' + addinfo + '|' + phone
                            if keys not in keys:
                                keys.add(key)
                                yield [website, loc, name, addinfo, address, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
