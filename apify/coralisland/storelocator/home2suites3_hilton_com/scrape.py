import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.hilton.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.hilton.com/graphql/customer?pod=brands&type=GetFilteredLocations"
    session = requests.Session()
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'cookie': 's_ecid=MCMID%7C67516453094181265640690360565459043532; visitorId=9a40b77b-60b1-414f-a67a-71830d0f1846; dtCookie==3=srv=4=sn=D3BC65AD7FED251A8C258306FB44BFF6=perc=100000=ol=0=mul=1; d189805aa6dbab96f1c38fde021484c4=73f9b6ecb3dac78720aa7984529d5c58; akacd_ohw_prd_external=3744876210~rv=49~id=cb9dd19e2d895c49e5883dedd87e5b03; AMCVS_F0C120B3534685700A490D45%40AdobeOrg=1; 2198ba377cca6d6e1f3d66b3013526d8=7626511753c2c36a8b7fdb8175efce22; ak_bmsc=B6B139DE410A97B20CF8E7A01DA241E0ADDE943F146A000089996E5D750E3F02~pl5cxlcHQ5gPqI6vHHLBTMmIYgKG7Eww9ToGRcYrRk5XTu+vwrH+DmP9ckO0cORMfMME2r0COPsoamzQG1UlSHTiWJ4RIM2uKZtrvrIkzwZmFktUN7hfckInCb9GZSxKGcscIyjMZknRe9m7r5nMV0wSyOnctPwiAlJNmWA9VmNI+MuO+3GhbB6+EoKlXZ2qlMpRYPZ0Bwoic7uXhA/i71sgBk/6C6Y6bOluMRBcviz5s=; bm_sz=14E1E89F111A12608EB3CC6AC9BD0A02~YAAQP5TerTuFJOVsAQAAesEH+AQHZyv4sO+QI16hPAShKfFcv5R1p5cApdK83Piy06IrIZUPvjwGfYJ8k6/p9WEo4lI0gF/j5kta5fOs4M0YM/fbBUYBLSQZluwlU6d23IP3m11qKh1vKbbILg7YBkA6SsBOzlb3rys48qadO5OUcf93LD671nJJwUofzH/P; AKA_A2=A; AMCV_F0C120B3534685700A490D45%40AdobeOrg=-1303530583%7CMCIDTS%7C18142%7CMCMID%7C67516453094181265640690360565459043532%7CMCAID%7CNONE%7CMCOPTOUT-1567536606s%7CNONE%7CvVersion%7C3.3.0; GWSESSIONID=lYmGdnhPZJW6T21Cs2p8m2hkNMGrQ2Hhj1yZgpNdGWgMrDMLp2JF!1408797365; smtrsession=currentProdID%7CDALASHW; _dpm_ses.12a2=*; _dpm_id.12a2=c5e01563-9c14-4c91-a22e-f3838d11cad4.1564786085.5.1567529547.1567423546.d8ee6833-fd15-4d5d-9e4d-ee818a476f19; TS01b027a7=012a9818ce0be1383b2f653ef52fbd0e22a538a43dfbb8e42833cf4bd1bb0fbb5efaa243c87ce0629f8466393e4da291ec4c9d667ecfbcf87aca0ed7fdc1dc9b5281af988a; _abck=5CF036E3B13EF4297EABAD851BBB852B~0~YAAQP5TereCJJOVsAQAAH/kS+AI6tNkAvd0yNvd7zLScOOH+F+jYuYZgAa/RTuiG87KeJrRacE+NRehI/UQFkogFKqpHlkzakdo0E0lrmiQsDzgpjHynGFg0xvHYH+wlOBggXk5FvAI0B+A2SKSr6ug/VVIUU/XnwFJN264m4hm72aIf9Wj40+Okf3y8Yr25OSS0zesfhtwconI06n8NdYBoDfJZXBfIALk1QwiJo0Jy8BvEWPzGIiqZfY6Iku+wqDef+r6B4QF2Sb4C4dy2yJxEe0/H31nUpiq13FSEnI8aWNpgp5K65W8=~-1~-1~-1; bm_sv=5DC1069811394AB2677F2DD53EBBA7B5~QZum/o4WyuFo0Ck/s5Bw5m1FdYF1coueAUW0xFFNCiY5SazaL/gWGEYP8EJrnnsCj6Q+49zNPi+tbA6btQ6MtrXVXwxecJatzstYRUiSpVkxphiWUSsQhE4ufXVk+BYpexC0rTe1HFAray9AYDJzKTK08jWyxwQtxdQVkx+jAyo=; forterToken=b19f26c2cdbf4509950f33ed07d0394b_1567530056464_378_UAL9_9ck',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    payload = {
        "operationName":"GetFilteredLocations",
        "variables":{
            "brandCode":"HT",
            "language":"en",
            "boundingBox":{
                "ne":{
                    "latitude":"75.27640552816561",
                    "longitude":"-38.45954779857945"
                },
            "sw":{
                "latitude":"-27.212082044335254",
                "longitude":"-168.53767279857945"
            }
        },
        "filters":[]
        },
        "query":"query GetFilteredLocations($filters: [HotelAmenityId!], $brandCode: String!, $boundingBox: HotelBoundingBoxInput!, $language: String!) {\n  hotels(amenityIds: $filters, brandCode: $brandCode, boundingBox: $boundingBox, language: $language) {\n    ctyhocn\n  }\n}\n"
    }
    request = session.post(url, data=json.dumps(payload), headers=headers)
    sid_list = json.loads(request.text)['data']['hotels']
    for sid in sid_list:        
        link = 'https://www.hilton.com/graphql/customer?pod=brands&type=GetHotelInfo'
        store_payload = {
            "operationName":"GetHotelInfo",
            "variables":{
                "ctyhocn":sid['ctyhocn'],
                "language":"en"
            },
            "query":"query GetHotelInfo($ctyhocn: String!, $language: String!) {\n  hotel(ctyhocn: $ctyhocn, language: $language) {\n    address {\n      addressFmt\n    }\n    brandCode\n    galleryImages(numPerCategory: 2, first: 12) {\n      alt\n      hiResSrc(height: 430, width: 950)\n      src\n    }\n    homepageUrl\n    name\n    open\n    openDate\n    phoneNumber\n    resEnabled\n    amenities(filter: {groups_includes: [hotel]}) {\n      id\n      name\n    }\n  }\n}\n"
        }
        store = json.loads(session.post(link, data=json.dumps(store_payload), headers=headers).text)['data']['hotel']
        output = []
        output.append(base_url) # url
        if store:
            output.append(get_value(store['name'])) #location name
            address = eliminate_space(validate(store['address']['addressFmt']).split(','))
            if len(address) >= 5:
                output.append(validate(address[:-4])) #address
                output.append(address[-4]) #city
                output.append(address[-3]) #state
                output.append(address[-2]) #zipcode
                output.append(address[-1]) #country code
                output.append('<MISSING>') #store_number
                output.append(get_value(store['phoneNumber']).replace('+', '')) #phone
                output.append('Homewood Suites by Hilton | Extended Stay Hotels') #location type
                output.append('<INACCESSIBLE>') #latitude
                output.append('<INACCESSIBLE>') #longitude
                output.append('<MISSING>') #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
