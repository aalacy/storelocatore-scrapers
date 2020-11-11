from bs4 import BeautifulSoup
import csv
import string
import re, time, json

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
    # Your scraper here
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.seasons52.com/site-map'
    r = session.get(url, headers=headers, verify=False)
    storelist = []
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.select("a[href*=locations]")
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:
        if p == 0:
            link = 'https://www.seasons52.com/locations/fl/sunrise/sunrise-sawgrass/4548'
        else:
            link = 'https://www.seasons52.com'+div['href']
        if link.find('all-locations') == -1:           
            r = session.get(link, headers=headers, verify=False)
            loc = r.text.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0].replace('\n','')
            loc = json.loads(loc)
            #print(loc)
            if len(loc) > 0:
                address = loc['address']
                ccode = address['addressCountry']
                street = address['streetAddress']
                pcode = address['postalCode']
                city = address['addressLocality']
                state = address['addressRegion']
                phone = loc['telephone']
                lat = loc['geo']['latitude']
                longt = loc['geo']['longitude']
                hourslist= loc["openingHours"]
                title = loc['name']
                store = loc["branchCode"]
                if len(street) < 2:
                    soup = BeautifulSoup(r.text,'html.parser')
                    address = soup.find('input',{'id':"restAddress"})['value']                
                    street,city,state,pcode = address.split(',')
                    store= soup.find('input',{'id':"restID"})['value']
                    title = soup.find('h1').text
                    phone = soup.find('input',{'id':"togoFranchisePhoneNo"})['value']
                hours = ''
                for hr in hourslist:
                    day = hr.split(' ',1)[0]
                    start = hr.split(' ',1)[1].split('-')[0]
                    end = hr.split(' ',1)[1].split('-')[1]
                    check = (int)(end.split(':',1)[0])
                    if check > 12:
                        endtime = check - 12
                    hours = hours + day + ' '+ start + ' AM - '+ str(endtime) + ':' + end.split(':',1)[1]+' PM '
                hours = hours.replace('Mo','Monday').replace('Tu','Tuesday').replace('Th','Thursday').replace('We','Wednesday').replace('Fr','Friday').replace('Sa','Saturday').replace('Su','Sunday')     
                
            else:
                soup = BeautifulSoup(r.text,'html.parser')
                address = soup.find('input',{'id':"restAddress"})['value']                
                street,city,state,pcode = address.split(',')
                try:
                    lat,longt = soup.find('input',{'id':"restLatLong"})['value'].split(',')
                except:
                    continue
                store= soup.find('input',{'id':"restID"})['value']
                title = soup.find('h1').text
                phone = soup.find('input',{'id':"togoFranchisePhoneNo"})['value']
                hourlist = soup.find('div',{'class':'week-schedule'}).findAll('ul',{'class':'top-bar'})
                hours = ''
                for hr in hourlist:
                    try:
                        nowhr =  hr.find('li',{'class':'weekday'}).text+' '+ hr.find('li',{'class':'rolling-hours-start'}).text + ' '
                    except:
                        nowhr =  hr.find('li',{'class':'weekday-active'}).text+' '+ hr.find('li',{'class':'rolling-hours-start'}).text + ' '
                    
                    nowhr = nowhr.replace('Tue Nov 10 ','').replace(':00 EST 2020','').replace('\n', ' ')
                    hours = hours +nowhr
                    #print(nowhr)
                    #input()
                

            if store in storelist:
                continue
            storelist.append(store)
            data.append([
                        'https://www.seasons52.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('\xa0','').strip()
                    ])
            #print(p,data[p])
            p += 1
                
         
    return data

def scrape():
   
    data = fetch_data()
    write_output(data)

scrape()
