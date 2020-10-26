from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chemicalbank_com')



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
    # Your scraper here
    data = []
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://locations.tcfbank.com/api/mergelocations/getbyrectanglefilter?latitude=40.41553497314453&longitude=-82.70935821533203&swLatitude=37.07866682465554&swLongitude=-88.43388366699219&neLatitude=43.20260947193479&neLongitude=-76.89823913574219&count=900'
    
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()['Results']
    
    logger.info(len(loclist))
    
    for loc in loclist:
        #logger.info(loc)
        loc = loc['BankLocation']
        
        city = loc['Address']['City']
        pcode = loc['Address']['PostalCode']
        state = loc['Address']['State']
        street = loc['Address']['Street']
        store = loc['Id']
        ltype = loc['LocationType']
        title = loc['Name']        
        lat = loc['Coordinates'][0]
        longt  = loc['Coordinates'][1]
       
        hours = loc['HoursLobby']
        if ltype == 'ATM':
            hours = '<MISSING>'
        if len(hours) < 3:
            hours = '<MISSING>'
        link = 'https://www.tcfbank.com/locations/details/'+loc['FormttedUrlForDetailsPage']
        if ltype == 'Branch':
            phone = '(800) 823-2265'
        else:
            phone = '<MISSING>'
        if loc['AtmAtBranch'] == True:
            ltype = 'Branch | ATM'
        if hours != '<MISSING>':    
            data.append([
                    'https://chemicalbank.com/',
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
            #logger.info(p,data[p])
            p += 1
            
       
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

