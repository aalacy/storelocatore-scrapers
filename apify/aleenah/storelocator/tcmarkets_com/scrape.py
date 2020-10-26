import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress
import re

def get_value(item):
    if item == None or len(item) == 0:
        item = '<MISSING>'
    return item

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '')
        else:
            street += addr[0].replace(',', '') + ' '
    return {
        'street': get_value(street),
        'city' : get_value(city),
        'state' : get_value(state),
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()

all=[]

def fetch_data():
    # Your scraper here


    res = session.get("https://tcmarkets.com/store-finder/")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find_all('a', {'itemprop': 'url'})

    del stores[0]
    for store in stores:
        url=store.get('href')
        print(url)
        if 'https://tcmarkets.com/store-finder/dixon-ace-hardware/' in url:
            continue
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data = soup.find('div', {'class': 'fl-rich-text'}).find_all('p')
        #data=re.findall(r'Store Address([a-zA-Z0-9,\.\(\)\- #&\']+)Store Hours:([a-zA-Z0-9\. \-:]+)',str(soup).replace('<strong>','').replace('</p>','').replace('<p>','').replace('\n','').replace('</strong>','').replace('<br>','').replace('<br/>','').replace('\xa0','').replace('&nbsp;','').replace('Services Offered:',''))[0]

        for p in data:
            if 'Store Address' in p.text:
                addr=p
        phone=""
        if 'Hours' not in addr.text:
            ad = addr
            tim = data[data.index(addr) + 1].text.strip()
            addr=addr.text.strip()
            p = re.findall(r'\([\d]{3}\)[\d \-]+', tim)
            print(p)
            if p != []:
                phone = p[0]
                
                tim = data[data.index(ad) + 2].text.strip()
        else:

            addr=addr.text.strip()
            tim = re.findall('Store Hours:(.*)', addr, re.DOTALL)[0]

            addr = addr.replace(tim, '')

        if phone=='':
            phone = re.findall(r'\([\d]{3}\)[\d \-]+',addr)[0]

        tim=' '.join(tim.replace('Store Hours:','').strip().split('\n'))
        addr=' '.join(addr.replace('Store Address','').replace(phone,'').strip().split('\n'))
        parsed_address = parse_address(addr)
        city = parsed_address['city']
        state = parsed_address['state']
        zip = parsed_address['zipcode']
        street = parsed_address['street']

        loc=city
        if loc=='<MISSING>':
            loc=url.strip().strip('/').split('/')[-1].replace('-',' ').upper()


        all.append([

            "https://tcmarkets.com",
            city,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            url])



    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
