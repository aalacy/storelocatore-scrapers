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
        # 'authorization': 'Basic c182dlhYaFRmMnk0SzJpTThmNm9vUVRTMDQ4YTpmVDNvNWMwcTJtcl9vMUxFck00X1ZTZDBQQ2th',
        'content-type': 'application/json',
        'cookie': 's_ecid=MCMID%7C67516453094181265640690360565459043532; visitorId=9a40b77b-60b1-414f-a67a-71830d0f1846; dtCookie==3=srv=4=sn=D3BC65AD7FED251A8C258306FB44BFF6=perc=100000=ol=0=mul=1; d189805aa6dbab96f1c38fde021484c4=73f9b6ecb3dac78720aa7984529d5c58; akacd_ohw_prd_external=3744876210~rv=49~id=cb9dd19e2d895c49e5883dedd87e5b03; AMCVS_F0C120B3534685700A490D45%40AdobeOrg=1; 2198ba377cca6d6e1f3d66b3013526d8=7626511753c2c36a8b7fdb8175efce22; GWSESSIONID=wppJds8bJTFcyz4tlQLVnZZQB1hy9jyt1mZZhy6LjkY8flhppYh7!933675003; _dpm_id.12a2=c5e01563-9c14-4c91-a22e-f3838d11cad4.1564786085.4.1567423546.1567227952.b00d9c5f-9da7-4151-81e7-75ee836f887e; TS01b027a7=012a9818ce41ac10059e27be249248a8c747259c7c030c13bbef6abe22abd00f21d03a17d3ebb00fb7277e2f73ce04d55e934394254eefb2f549757e9141afc40f328fe6f1; _abck=5CF036E3B13EF4297EABAD851BBB852B~0~YAAQT5TerZvKvtpsAQAA6YQX9AIo+8/Y3iyTwEJQuGJ9d933U8kH3X6oWjltlhESHYi6eIxYZW3nczd8ubhIT78ID1eoT8gOJt2EJP1ORvJXYVt4zzIJjvL4JNwtCzwPtP7Py8DvKkoK3onatpHPlPc8WU4LXQPAIEC05aYXyP/J1s7jsZpk+tTyYR5ZnhsmytSLcdbzldIBGthP4lthbRm5Mbchi1976QI2NkkXQwM2Mj54cERlLDeRwSex9J988ZvLavZhwlHmkaE3FaQD9yH103M7/y00LSrr9GuTj2Jxcq9/5RCdJTQ=~-1~-1~-1; bm_sz=C3057E0F69A477EDD87DAB134B591CBA~YAAQ4zwxF4K1b9FsAQAAwHb09gQiCgS2lLy4jFPy9VLzIrpF0futflYoP5ZX11pAYC5Ae7LPtCv51LJZm/+SKnySjIMKjPV6o1p1b4BAGV7/4TL27id1w54elCMFkQ3hkxEZwkA87u9ermDQ1EJPYWMEtGSFo3IE9zCoALIHp2ReioWqGfeGvJXyVeVFHTY=; AKA_A2=A; ak_bmsc=EC72A803FCE7E38290D78A4C2D86C430ADDE943F146A000010536E5DF2D61C6F~plHfm1ZS+oFlGsJLG9H+GW4L0uFV26RrSiY5OGUlpTcvuThvEbw8fhGt9ta4kO9R5faozBi6YSznLLG+eSjRBMZwzKaDxMicVPYKotZzeMSVqWso69/afjxorP1qAi0CoDLvob0JyuTOig1H4SUf8wiq5wgIfzfr8b493UY710VVZTCuH8pjsiuN14w9YXtmFZZpEFQ9Q2Pk62yDyneH52PfDdcaoU3KdIuUAQ2A2diQc=; AMCV_F0C120B3534685700A490D45%40AdobeOrg=-1303530583%7CMCIDTS%7C18142%7CMCMID%7C67516453094181265640690360565459043532%7CMCAID%7CNONE%7CMCOPTOUT-1567518475s%7CNONE%7CvVersion%7C3.3.0; forterToken=b19f26c2cdbf4509950f33ed07d0394b_1567511285127_297_UAL9_9ck',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    payload = {
        "operationName":"GetFilteredLocations",
        "variables": {
            "brandCode":"HW",
            "language":"en",
            "boundingBox":{
                "ne":{
                    "latitude":"74.40347187339319",
                    "longitude":"-17.458984375"
                },
                "sw":{
                    "latitude":"-30.14091616176065",
                    "longitude":"-176.541015625"
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
