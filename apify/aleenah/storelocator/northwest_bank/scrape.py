from bs4 import BeautifulSoup
import csv
import string
import re, time,usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('northwest_bank')



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
    
    data = []
    titlelist = []
    titlelist.append('none')
    p = 0
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    for statenow in states:
        #statenow = 'DC'
        
        gurl = 'https://maps.googleapis.com/maps/api/geocode/json?address='+statenow+'&key=AIzaSyCT4uvUVAv4U6-Lgeg94CIuxUg-iM2aA4s&components=country%3AUS'
        r = session.get(gurl, headers=headers, verify=False).json()
        if r['status'] == 'REQUEST_DENIED':
            pass
        else:
            coord = r['results'][0]["geometry"]['location']
            latnow = coord['lat']
            lngnow = coord['lng']
            link ='https://www.northwest.bank/locations?state='+statenow+'&latlng='+str(latnow)+','+str(lngnow)+'&distance=1000&type=branch'
            #logger.info(link)
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            try:
                loclist = soup.find('div',{'class':'branches'}).findAll('li')
            except:
                continue
            #logger.info(len(loclist))
            for loc in loclist:
                title = loc.find('h4').text
                address = loc.find('p',{'class':'address'}).text.replace('\n',' ').lstrip()
                address = usaddress.parse(address)
                i = 0
                street = ""
                city = ""
                state = ""
                pcode = ""
                while i < len(address):
                    temp = address[i]
                    if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                        street = street + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        pcode = pcode + " " + temp[0]
                    i += 1

                street = street.lstrip().replace(',','')
                city = city.lstrip().replace(',','')
                state = state.lstrip().replace(',','')
                pcode = pcode.lstrip().replace(',','')
                phone = loc.find('a',{'class':'phone'}).text
                try:
                    hours = loc.find('div',{'class':'info'}).text.lstrip().split('\n',1)[1].split('Drive',1)[0].replace('\n',' ').strip()
                except:
                    hours = loc.find('div',{'class':'info'}).text.split('\n',1)[1].replace('\n',' ').strip()
                try:
                    hours = hours.split('Deposit')[0]
                except:
                    pass
                try:
                    hours = hours.split('Fax')[0]
                except:
                    pass
                try:
                    hours = hours.split('Coin')[0]
                except:
                    pass
                if pcode.strip()=='466001':
                    pcode = '46628'
                hours = hours.replace('\u200b','').replace('\xa0','').replace('Hours: ','')
                lat,longt  = loc.find('div',{'class':'info'}).find('a')['href'].split('%40',1)[1].split('%2C',1)
                longt = longt.split('%2C',1)[0]
               
                if street in titlelist:
                    continue
                    
                else:
                    titlelist.append(street)
                    data.append([
                            'https://www.northwest.bank/',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            'US',
                            '<MISSING>',
                            phone,
                            'Branch',
                            lat,
                            longt,
                            hours
                        ])
                    #logger.info(p,data[p])
                    p += 1
                    #input()
                    
        break
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
