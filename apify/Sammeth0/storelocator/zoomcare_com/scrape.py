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
    url = 'https://www.zoomcare.com/about'
    r = session.get(url, headers=headers, verify=False)
    linklist = []
    soup =BeautifulSoup(r.text, "html.parser")  
    divlist = r.text.split('\\u002Fclinic\\u002Fzoomcare')   
    p = 0
    for div in divlist:
        link = 'https://www.zoomcare.com/clinic/zoomcare'+div.split('"')[0]  
        
        if link.find('clinic/zoomcare') > -1 and link.find('html') == -1:           
            if link in linklist:
                continue
            linklist.append(link)
            #print(link)
            r = session.get(link , headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            title = soup.find('title').text
            try:
                title = title.split(' |')[0]
            except:
                pass
            address = soup.find('div',{'class':'clinic-address'}).findAll('div')
            street = address[0].text
            city, state = address[1].text.split(', ')
            try:
                state,pcode = state.lstrip().spliy(' ',1)
            except:
                pcode = '<MISSING>'
            hours = soup.find('div',{'class':'Clinic__body__hours'}).text
            try:
                coord = soup.find('iframe',{'class':'Clinic__body__maps-iframe'})['src']
                lat,longt = coord.split('sll=',1)[1].split('&',1)[0].split(',')
            except:
                lat = longt = '<MISSING>'
            phone = '<MISSING>'
            data.append([
                        'https://www.zoomcare.com',
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
                        hours.replace('\n','').strip()
                    ])
            #print(p,data[p])
            p += 1
                
      
           
        
    return data


def scrape():
  
    data = fetch_data()
    write_output(data)
    
scrape()
