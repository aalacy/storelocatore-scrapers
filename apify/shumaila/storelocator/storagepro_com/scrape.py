from bs4 import BeautifulSoup
import csv
import string,json
import re, time, usaddress

from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
headers1 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'tenantapi.com',
            'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjI4MDczNjkiLCJhcCI6IjgyNzU0OTI1OSIsImlkIjoiZjdhOWZkMjg0ZWVlODllZSIsInRyIjoiM2I4ZTkxMGZmNDQ4YWEwOTY5NDIyYjg5YTdhN2Q1MzAiLCJ0aSI6MTYwNTg3MTQzNzgyM319',
            'Origin': 'https://www.storagepro.com',
            'Referer': 'https://www.storagepro.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'X-storageapi-date': '1605871437',
            'X-storageapi-key': '8651844f76294d9f9ce61ac39ae0d33f',
            'X-storageapi-trace-id': '83f3aa24-e03e-42ab-822d-47577cfc9d54'}

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
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    statelist =[]
    streets = []
    url = 'https://www.storagepro.com/'
    r = session.get(url,headers = headers, verify=False)
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.select("a[href*=storage-units]")
    hidden = r.text.split('hiddenCities:',1)[1].split('}',1)[0]
    hidden = hidden+'}'
    hidden = hidden.split('],')
    hstates = []   
    for hd in hidden:
        state = hd.split(':',1)[0].replace('{','').replace('"','')
        url = 'https://tenantapi.com/v3/applications/app72d8cb0233044f5ba828421eb01e836b/v1/search/owners/own3635fb2e825d49a9a7a9f8d9bcdcd304/?&lat=&lon=&ip=&address='+state+'&state=&filter_storage_type=undefined&filter_unit_size=&filter_distance_max=13&filter_distance_min=0&filter_price_max=500&filter_price_min=0&list_all=false'
        loclist = session.get(url, headers=headers1, verify=False).json()['applicationData']['app72d8cb0233044f5ba828421eb01e836b'][0]['data']
        for loc in loclist:
            statelist.append(loc['landing_page_url'])
    
    for div in divlist:
        divlink = 'https://www.storagepro.com' + div['href']
        if divlink in statelist:
            continue
        statelist.append(divlink)
       
    p = 0
    for div in statelist:
        divlink = div
        #print("mml",divlink)
        try:
            r = session.get(divlink, headers=headers, verify=False)
        except:
            continue
        time.sleep(2)
        soup = BeautifulSoup(r.text,'html.parser')
        linklist = soup.findAll('a',{'class':'location-link'})
        #print(len(linklist))
        #input()
        flag = 0
        if len(linklist) == 0:
            linklist.append(div)
            flag =1
            
        for link in linklist:

          
            if flag == 0:                
           
                link =  'https://www.storagepro.com' + link['href']
                #print("ll",link)
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text,'html.parser')
                link = r.url
            
            #print(link)
           
            det = soup.find('div',{'class':'facility-card'})
            try:
                title = det.find('h2').text
            except:
                continue
            address = det.find('div',{'class':'facility-address'}).text.replace('\n',' ').strip().replace('Located off','')
            try:
                phone = det.find('a',{'class':'phone'}).text.replace('\n','').strip()
            except:
                phone = '<MISSING>'
            try:
                hours = det.find('div',{'class':'office-hours'}).text
            except:
                hours = '<MISSING>'
            try:
                lat,longt = soup.find('div',{'class':'google-map'}).find('img')['src'].split('center=',1)[1].split('&',1)[0].split(',')
            except:
                lat = longt = '<MISSING>'
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
            try:
                state,chk = state.strip().split(' ',1)
                pcode = chk+' '+pcode
            except:
                pass
            if len(pcode) > 5:
                ccode = "CA"
            else:
                ccode= 'US'
            if len(hours) < 3:
                hours = '<MISSING>'
            if street in streets:
                continue
            
            streets.append(street)
            ltype = 'Store'
            if link.find('storagepro.com') == -1:
                ltype = 'Facility Partner'
            if state == 'BC':
                ccode = 'CA'
            if len(state) < 2 and len(city) < 3 and 'Helena MT' in street:
                city = 'Helena'
                state = 'MT'
                street = street.replace('Helena MT','')
                
            data.append([
                        'https://www.storagepro.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        '<MISSING>',
                        phone,
                        ltype,
                        lat,
                        longt,
                        hours.replace('AM',' AM ').replace('PM',' PM ').replace('Closed','Closed ')
                    ])

            #print(p,data[p])
            p += 1
                    
    
    return data


def scrape():  
    data = fetch_data()
    write_output(data)
   

scrape()
