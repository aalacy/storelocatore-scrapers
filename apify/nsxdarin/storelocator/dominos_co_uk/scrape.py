import csv
from sgrequests import SgRequests
from tenacity import retry
from tenacity import stop_after_attempt

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

@retry(stop=stop_after_attempt(10))
def get_result(url, headers):
    global session
    try:
        return session.get(url, headers=headers)
    except:
        session = SgRequests()
        raise

def fetch_data():
    global session
    for x in range(27500, 30000):
        if x % 10 == 0:
            session = SgRequests()
        url = 'https://www.dominos.co.uk/storefindermap/getstoredetails?PostCode=London&StoreId=' + str(x)
        r = get_result(url, headers=headers)
        loc = '<MISSING>'
        website = 'dominos.co.uk'
        typ = '<MISSING>'
        hours = ''
        store = x
        phone = ''
        name = ''
        for raw_line in r.iter_lines(decode_unicode=True):
            line = str(raw_line)
            if '"name":"' in line:
                name = line.split('"name":"')[1].split('"')[0]
                lat = line.split('"latitude":"')[1].split('"')[0]
                lng = line.split('"longitude":"')[1].split('"')[0]
                add = line.split('"address1":"')[1].split('"')[0] + ' ' + line.split('"address2":"')[1].split('"')[0]
                add = add.strip()
                city = line.split('"address3":"')[1].split('"')[0]
                state = '<MISSING>'
                zc = line.split('"postCode":"')[1].split('"')[0]
                country = 'GB'
                phone = line.split('"telephone":"')[1].split('"')[0]
                days = line.split('"openingHours":[')[1].split(']')[0].split('"day":"')
                for day in days:
                    if 'abbreviatedDay' in day:
                        hrs = day.split(',"abbreviatedDay":"')[1].split('"')[0] + ': ' + day.split('"openingTime":"')[1].split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if name != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
