from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest'

           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    states = {'AL':"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado",
    "CT":"Connecticut","DC":"DC","DE":"Delaware","FL":"Florida","GA":"Georgia",
    "HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas",
    "KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan",
    "MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana", "NE":"Nebraska","NV":"Nevada",
    "NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York", "NC":"North Carolina","ND":"North Dakota",
    "OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania", "RI":"Rhode Island","SC":"South Carolina",
    "SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah",  "VT":"Vermont","VA":"Virginia"
    ,"WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}
                 
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://www.cubesmart.com/facilities/query/GetSiteGeoLocations'
    p = 0
    storelist = []
    loclist = session.post(url,headers=headers).json()
    for loc in loclist:
        
        store = str(loc['Id'])
        street = loc['Address']
        title = 'Self Storage of '+ loc['City']
        city = loc['City'].lower().strip().replace(' ','-')
        nowstate = loc['State']
        state = states[nowstate].lower().strip().replace(' ','-')
        lat = loc['Latitude']
        longt = loc['Longitude']        
        link = 'https://www.cubesmart.com/'+state+'-self-storage/'+city+'-self-storage/'+store+'.html'
        if street in storelist:
            continue
        #print(link)
        storelist.append(street)
        r = session.get(link,headers=headers).text
        try:
            pcode = r.split(',"postalCode":"',1)[1].split('"',1)[0]
        except:
            continue
        phone = r.split('},"telephone":"',1)[1].split('"',1)[0]
        try:
            hours = r.split('<p class="csHoursList">',1)[1].split('</p>',1)[0].replace('&ndash;',' - ').replace('<br>',' ').lstrip()
        except:
            hours = '<MISSING>'
        if pcode == '75072':
            pcode ='75070'
   
        if str(loc['OpenSoon']) == 'False':
            data.append([
                'https://www.cubesmart.com/',
                link,                   
                title,
                street,
                str(loc['City']),
                str(loc['State']),
                pcode,
                'US',
                store,
                phone,
                '<MISSING>',
                lat,
                longt,
                hours
            ])
            #print(p,data[p])
            p += 1
        


    

                
        
    return data


def scrape(): 
    data = fetch_data()
    write_output(data)

scrape()

