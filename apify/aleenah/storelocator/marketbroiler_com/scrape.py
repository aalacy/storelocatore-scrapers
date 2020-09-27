from bs4 import BeautifulSoup
import csv
import string
import re, time

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
    url = 'https://www.marketbroiler.com/copy-of-locations'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")   
    linklist = soup.findAll('a', {'class': "wixAppsLink"})   
    #print("states = ",len(linklist))    
    p = 0
    for link in linklist:
        if link['href'].find('location') > -1 or link['href'].find('map') > -1:
                continue
        else:
            title = link.text
            link = link['href']            
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            #print(soup.text)
            #input()
            content = soup.text.split('FRESH FISH MARKET & TAKE-OUT')[1].split('No')[0].lstrip()
            
            try:
                content = content.split('DIRECTION')[0]
            except:
                pass
            #print(content)
            try:
                phone = content.split('Phone.')[1].lstrip()
                address = content.split('Phone')[0]
                street = address.split(')')[0] +')'
                city = address.split(')')[1].split(', ')[0]
                state,pcode = address.split(', ')[1].split(' ',1)
                
            except:
                phone = content.splitlines()[-1]
                content= content.splitlines()
                i = 0
                street  = content[i]
                i += 1
                if content[i].find('(') > -1:                    
                    street  = street + ' '+ content[i]
                    i += 1
                
                city,state = content[i].split(', ')
                state ,pcode = state.lstrip().split(' ',1)
               

            try:
                phone = phone.split('Hours')[0]
            except:
                pass
            
            try:
                hours = soup.text.split('DAILY',1)[1].split("HAPPY")[0]
            except:
                hours = 'Mon' + soup.text.split('Mon',1)[1].split("Join")[0]
            try:
                hours = hours.split('ALL')[0]
            except:
                pass
            try:
                hours = hours.split('REO')[0]
            except:
                pass

            hours = re.sub(pattern,' ',hours) .lstrip().replace('\n',' ')
            iframe = soup.findAll('iframe',{'name':'htmlComp-iframe'})[1]['data-src']           
            try:
                r = session.get(iframe, headers=headers, verify=False)
                longt,lat = r.text.split('!2d')[1].split('!2m')[0].split('!3d')
            except:               
                
                iframe = soup.findAll('iframe',{'name':'htmlComp-iframe'})[0]['data-src']               
                try:
                    r = session.get(iframe, headers=headers, verify=False)
                    longt,lat = r.text.split('!2d')[1].split('!2m')[0].split('!3d')
                except:
                    lat = '<MISSING>'
                    longt = '<MISSING>'
            try:
                lat = lat.split('!3m')[0]
            except:
                pass
        
            data.append([
                        'www-marketbroiler-com',
                        link,                   
                        title,
                        street.replace('\u200b','').replace('\xa0 ',''),
                        city.replace('\u200b',''),
                        state.replace('\u200b',''),
                        pcode.replace('\u200b',''),
                        'US',
                        '<MISSING>',
                        phone.replace('\u200b',''),
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('\u200b','')
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
