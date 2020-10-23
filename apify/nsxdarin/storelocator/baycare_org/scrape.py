import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('baycare_org')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    for x in range(0, 15):
        logger.info(('Page %s...' % str(x)))
        url = 'https://baycare.org/api/search/locations?&page=' + str(x) + '&pageSize=50&returnWildcardResults=true&searchDistance=500&FacilityType=Behavioral%20Health&FacilityType=Corporate&FacilityType=Community%20Blood%20Center&FacilityType=Diabetes%20Education&FacilityType=Emergency%20Center&FacilityType=Extended%20Care&FacilityType=Fitness%20Center&FacilityType=Health%20Centers&FacilityType=HealthHub&FacilityType=HomeCare&FacilityType=Hospital&FacilityType=Imaging&FacilityType=Lab%20Services&FacilityType=Medical%20Arts%20Building&FacilityType=Outpatient%20Facility&FacilityType=Outpatient%20Rehabilitation&FacilityType=Physician%20Specialty%20Group&FacilityType=Primary%20Care&FacilityType=Wound%20Care&FacilityType=Wellness%20Station&FacilityType=Walk-in%20Clinic&FacilityType=Urgent%20Care&FacilityType=Surgery%20Center&FacilityType=Specialty%20Center&FacilityType=Sleep%20Center'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        website = 'baycare.org'
        for line in r.iter_lines(decode_unicode=True):
            if '"locationId": "' in line:
                store = line.split('"locationId": "')[1].split('"')[0]
                name = ''
                city = ''
                state = ''
                zc = ''
                country = 'US'
                phone = ''
                lat = ''
                lng = ''
                typ = ''
                hours = ''
            if '"locationName": "' in line:
                name = line.split('"locationName": "')[1].split('"')[0]
            if '"locationFacilityType": "' in line:
                typ = line.split('"locationFacilityType": "')[1].split('"')[0]
            if '"locationUrl": "' in line:
                loc = 'https://baycare.org' + line.split('"locationUrl": "')[1].split('"')[0]
            if '"address1": "' in line:
                add = line.split('"address1": "')[1].split('"')[0]
                if ' Suite' in add:
                    add = add.split(' Suite')[0]
            if '"city": "' in line:
                city = line.split('"city": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                country = 'US'
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"locationHours": "' in line:
                hours = line.split('"locationHours": "')[1].split('"')[0]
            if '"locationLatitude": ' in line:
                lat = line.split('"locationLatitude": ')[1].split(',')[0]
            if '"locationLongitude": ' in line:
                lng = line.split('"locationLongitude": ')[1].split(',')[0]
            if '"phoneNumber": "' in line:
                phone = line.split('"phoneNumber": "')[1].split('"')[0]
            if '"saveYourSpotEnabled"' in line:
                hours = hours.replace('\\n',' ').replace('  ',' ').strip()
                if hours == '':
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
