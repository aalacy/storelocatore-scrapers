import csv
import urllib2
import requests
import json
import usaddress

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'authority': 'www.lecreuset.com',
           'path': '/store-locations',
           'cookie': 'CACHED_FRONT_FORM_KEY=Vly6nxYxMS6vCpnN; visid_incap_1361768=S/lSyDqVTWSuXY6NzigaBpBgW10AAAAAQUIPAAAAAABRSgqmnS0PBr0s8c/PodUf; nlbi_1361768=UDkMRNLkeXHWfKI3aaK2YgAAAAC6z+e7nqbILWAM+2lAkJnc; incap_ses_1165_1361768=5PLeWQDI2w/IUaRgrOkqEJBgW10AAAAAkSjldQKcMTRNcFkHk9yBvA==; _gcl_au=1.1.469104133.1566269583; _ga=GA1.2.451944638.1566269583; _gid=GA1.2.1819912753.1566269583; CUSTOMER_SEGMENT_IDS=4; frontend=81gpo6e6qgdd00v7k0argal404; frontend_cid=t15GksszBufPBrjh; ltkmodal-suppression-cd6d454e-4618-486b-af0a-541ed34ea670=Sun%20Nov%2017%202019%2021%3A53%3A03%20GMT-0600%20(Central%20Standard%20Time); _gaexp=GAX1.2.gP6sg8KEQ4GrQBh4s3KIQA.18189.1; GSIDrG1DvIsOHGMT=041ec277-655c-4329-9daf-5b92810b433e; STSID809263=80c88094-dc0f-43ac-a15d-f55ceb543133; _hjid=0a032c25-c2d1-42d0-b951-e518575c6b0e; _fbp=fb.1.1566269583885.690967470; __adroll_fpc=4c58791d5756888afb1911a3f4d90152-s2-1566269584062; _vuid=0182b02f-fe25-4408-b031-5649363cd9af; _hjIncludedInSample=1; addshoppers.com=2%7C1%3A0%7C10%3A1566269589%7C15%3Aaddshoppers.com%7C44%3AODQ0OWUzYzQxMjZhNDA5YWI2YmRmYjU3YTY1NDZjNGU%3D%7Cd2e24725e219cbaab0ae273e86536fef16fc36c7b2a69cecc5f331825f1e6954; cto_lwid=26205967-3fa8-4ab0-b8b7-960b2f489d1d; ltkmodal-impression-cd6d454e-4618-486b-af0a-541ed34ea670=4ea0d3ab-0f33-485a-9b21-0bd640d627a8; ltkpopup-session-depth=5-2; AWSALB=bsQJLm4evHpLTK5aADLEv1kvC3LNI+jtVVP/1270tg8YU5/KgFRGwbRs0cbOPVc7FnbwlRUGV+EVn6/18TPYD7aJlRJOpXybBlrDpnKS7Lwes/SmqQh6L5VQ2FES; _derived_epik=dj0yJnU9SHVOOVJ4RGFtTVNvSm1mY0pKM0EtdG5pMktWVTcxTFQmbj00bjAtY0MyY05mdmlzUThaSk5EcFhnJm09NyZ0PUFBQUFBRjFiWTFn; __ar_v4=LHY4VUSDXRDPLMHDUSGW4Z%3A20190819%3A18%7CH4M5JAF4OBAKZJBPZG7M6O%3A20190819%3A18%7CKEYDOKUWSRFTZGKTBAQYUF%3A20190819%3A18'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.lecreuset.com/store-locations'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'initial_locations:  ' in line:
            array = json.loads(line.split('initial_locations:  ')[1].split(']')[0] + ']')
            for item in array:
                website = 'lecreuset.com'
                typ = 'Store'
                country = item['country']
                name = item['title'].encode('utf-8')
                rawadd = item['address'].replace('\n',',').strip().encode('utf-8')
                if country == 'US':
                    try:
                        add = usaddress.tag(rawadd)
                        baseadd = add[0]
                        if 'AddressNumber' not in baseadd:
                            baseadd['AddressNumber'] = ''
                        if 'StreetName' not in baseadd:
                            baseadd['StreetName'] = ''
                        if 'StreetNamePostType' not in baseadd:
                            baseadd['StreetNamePostType'] = ''
                        if 'PlaceName' not in baseadd:
                            baseadd['PlaceName'] = '<INACCESSIBLE>'
                        if 'StateName' not in baseadd:
                            baseadd['StateName'] = '<INACCESSIBLE>'
                        if 'ZipCode' not in baseadd:
                            baseadd['ZipCode'] = '<INACCESSIBLE>'
                        address = add[0]['AddressNumber'] + ' ' + add[0]['StreetName'] + ' ' + add[0]['StreetNamePostType']
                        address = address.encode('utf-8')
                        if address == '':
                            address = '<INACCESSIBLE>'
                        city = add[0]['PlaceName'].encode('utf-8')
                        state = add[0]['StateName'].encode('utf-8')
                        zc = add[0]['ZipCode'].encode('utf-8')
                    except:
                        print('Address Not Tagged.')
                else:
                    address = '<INACCESSIBLE>'
                    city = '<INACCESSIBLE>'
                    state = '<INACCESSIBLE>'
                    zc = '<INACCESSIBLE>'
                if item['product_types'] != '':
                    typ = item['product_types']
                phone = item['phone']
                store = item['location_id']
                if item['store_hours']:
                    hours = item['store_hours'].replace('<strong>Hours<\/strong>\n','').strip().replace('\n',';').encode('utf-8')
                else:
                    hours = '<MISSING>'
                lat =  item['latitude']
                lng = item['longitude']
                if phone == '':
                    phone = '<MISSING>'
                if '>;' in hours:
                    hours = hours.split('>;')[1].strip()
                if country != '':
                    yield [website, name, rawadd, address, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
