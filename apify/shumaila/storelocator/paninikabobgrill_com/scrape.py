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
    # Your scraper here
    data = []
    pattern = re.compile(r'\s\s+') 
    linklist = []
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://paninikabobgrill.com/wp-admin/admin-ajax.php?action=store_search&lat=34.05223&lng=-118.24368&max_results=25&search_radius=50&autoload=1'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    loclist = r.json()
    url = 'https://paninikabobgrill.com/locations/'
    r = session.get(url, headers=headers, verify=False)
    soup= BeautifulSoup(r.text,'html.parser')
    storelist = soup.findAll('div',{'class':'location-item'})
   
        
    coordlist = r.text.split('locArray.push(',1)[1].split('let actualLon')[0]
    coordlist = '['+re.sub(pattern, ' ', coordlist).replace('); locArray.push(',',').replace(');','').replace(', }','}').replace("'",'"').rstrip() +']'
    coordlist = json.loads(coordlist)
    
    #print(coordlist)
    for div in storelist:
        address = div.find('div',{'class':'locations-footer'}).find('a')['href'].split('dir//')[1].replace('Panini Kabob Grill ','')
        street = address.split(', ')[0]   
        link = div.find('a',{'class':'location-url'})['href'].strip()
        title = div.find('h3').text.strip()
        phone = div.find('div',{'class':'location-phone'}).text.replace('\t','').replace('\n','').strip()
        address = div.find('div',{'class':'locations-footer'}).find('a')['href'].split('dir//')[1]
        #print(address)
        street,city,state= address.split(', ')
        state,pcode = state.lstrip().split(' ',1)
        lat = '<MISSING>'
        longt = '<MISSING>'        
        
        hours = '<MISSING>'
        store = '<MISSING>'
        for loc in loclist:
            if loc['store'] == title:
                hourlist = BeautifulSoup(loc['hours'],'html.parser')
                hours = re.sub(cleanr,' ',str(hourlist)).replace('  ',' ').strip()
                store = loc["id"]
                lat = loc['lat']
                longt = loc['lng']
                #print('Yes')
                break

        if lat ==  '<MISSING>':        
            for coord in coordlist:            
                if title.lower().find(coord['name'].lower().replace('-',' ')) > -1:
                    #print(title,coord['name'])
                    lat = coord['latitude']
                    longt = coord['longitude']
                    break
        if hours == '<MISSING>':             
            r1 = session.get(link, headers=headers, verify=False)
            soup1= BeautifulSoup(r1.text,'html.parser')
            hours = soup1.find('div',{'id':'hours'}).text.replace('\n','').replace('Hours:','').strip()
            #print('No')
            
        data.append([
                'https://paninikabobgrill.com/',
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

