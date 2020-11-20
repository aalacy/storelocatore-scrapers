from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
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
    p = 0
    data = []
    titlelist = []
    cleanr = re.compile(r'<[^>]+>')
    states = ["Georgia",'North Carolina', 'South Carolina','Virginia']
    for statenow in states:
        #print(statenow)
        gurl = 'https://maps.googleapis.com/maps/api/geocode/json?address='+statenow+'&key=AIzaSyCT4uvUVAv4U6-Lgeg94CIuxUg-iM2aA4s&components=country%3AUS'
        r = session.get(gurl, headers=headers, verify=False).json()
        if r['status'] == 'REQUEST_DENIED':
            pass
        else:
            coord = r['results'][0]["geometry"]['location']
            latnow = str(coord['lat'])
            lngnow = str(coord['lng'])
        url = 'https://southstatebank.com/api/locationsearch/Index?lat='+latnow+'&lng='+lngnow+'&searchQuery='+statenow+'&pageNum=10'
        #print(url)
        loclist = session.get(url, headers=headers, verify=False).json()["Entities"]
        
        for loc in loclist:            
                        
            lat = loc['YextDisplayCoordinate']['Latitude']
            longt = loc['YextDisplayCoordinate']['Longitude']
            street = loc['Address']['Line1']
            city = loc['Address']['City']
            state = loc['Address']['Region']
            pcode = loc['Address']['PostalCode']
            store = loc["Meta"]['Id']
            phone = loc['MainPhoneForDisplay']
            link = 'https://southstatebank.com/global/location-detail/'+str(store)+'/'+loc['NameForUrl']
            ltype = 'Branch'
            title = city+', '+state
            hours = ' '.join(loc["LobbyHours"])
            if str(loc['IsAtmOnly']).lower() == 'false':
                pass
            else:
                ltype = 'ATM'
            if len(hours) <3:
                hours = '<MISSING>'
            if store in titlelist:
                continue
            titlelist.append(store)
            data.append([
                    'https://southstatebank.com/',
                    link,                   
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    'US',
                    store,
                    phone,
                    ltype,
                    lat,
                    longt,
                    hours
                ])
            #print(p,data[p])
            p += 1
            


        
                
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

