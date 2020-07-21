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
    p = 0
    url = 'https://www.moncler.com/us/storeslocator'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    country_list = soup.findAll('a',{'class':'Directory-listLink'})
    
    for country in country_list:
        if country['href'].find('storeslocator/canada') > -1 or country['href'].find('storeslocator/united-states') > -1:            
            cclink = 'https://www.moncler.com' + country['href'].split('..')[1]
            ccode = 'US'
            if country['href'].find('storeslocator/canada') > -1 :
                ccode = 'CA'
            r = session.get(cclink, headers=headers, verify=False)  
            soup =BeautifulSoup(r.text, "html.parser")
            citylist = soup.findAll('a',{'class':'Directory-listLink'})
            for city in citylist:
                clink = 'https://www.moncler.com/us'+city['href'].split('../us')[1]
                r = session.get(clink, headers=headers, verify=False)  
                soup =BeautifulSoup(r.text, "html.parser")
                branchlink = soup.findAll('a',{'class':'Teaser-titleLink'})
                for branch in branchlink:
                    link = 'https://www.moncler.com/us'+branch['href'].split('../us')[1]
                    r = session.get(link, headers=headers, verify=False)  
                    soup =BeautifulSoup(r.text, "html.parser")
                    title = soup.find('h1').text
                    street= soup.find('span',{'class':'c-address-street-1'}).text.replace('\n',' ')
                    city = soup.find('span',{'class':'c-address-city'}).text
                    state = soup.find('abbr',{'itemprop':'addressRegion'}).text
                    pcode = soup.find('span',{'class':'c-address-postal-code'}).text
                    try:
                        phone = soup.find('div',{'id':'phone-main'}).text
                    except:
                        phone = '<MISSING>'
                    try:
                        hours = soup.find('table',{'class':'c-hours-details'}).text
                        hours = hours.split('Hours')[1].replace('Monday','Monday ').replace('Tuesday',' Tuesday ').replace('Wednesday',' Wednesday ').replace('Thursday',' Thursday ').replace('Friday',' Friday ').replace('Saturday',' Saturday ').replace('Sunday',' Sunday ')
                    except:
                        hours = '<MISSING>'
                    lat = soup.find('meta',{'itemprop':'latitude'})['content']
                    longt = soup.find('meta',{'itemprop':'longitude'})['content']
                    data.append([
                        'https://www.moncler.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
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
