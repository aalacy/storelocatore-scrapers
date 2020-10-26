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
    data = []
    p= 0
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    #link = 'https://rubytuesday.com/locations?locationId=4669'
    link = 'https://rubytuesday.com/locations?address=AL'
    count = 1
    while True:        
        r = session.get(link)        
        soup =BeautifulSoup(r.text, "html.parser")
        #print(soup)
        divlist = soup.findAll('div',{'class':'restaurant-location-item'})
        #print(len(divlist))
        for div in divlist:
            title = div.find('h1').text
            address = div.find('address').text.lstrip().splitlines()
            street = address[0]
            city = address[1].lstrip().replace(',','')
            state = address[2].lstrip()
            pcode = address[3].lstrip()            
            phone = div.find('a').text.strip()
            if phone.find('-') == -1:
                phone = phone[0:3]+'-'+phone[3:6]+'-'+phone[6:10]
            hourlist = div.find('table').findAll('tr',{'class':'hourstr'})
            hours = ''
            for hr in hourlist:
                hrday = hr.findAll('td')[0].text
                hrtime = hr.findAll('td')[1].text
                start = hrtime.split('-')[0] + ':00 AM -'
                temp = (int)(hrtime.split('-')[1].split(':')[0] )
                if temp > 12:
                    temp = temp -12
                end = str(temp) + ':00 PM '
                hours = hours + hrday +' ' + start +' '+ end
                
                
                   
            store = div['id'].split('-')[1]
            coord = div.find('div',{'class':"map_info"})
            lat = coord['data-lat']
            longt = coord['data-lng']         
            
            data.append([
                        'https://rubytuesday.com/',
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
            #input()
        try:
            nextlink = soup.find('ul',{'class':'pages'}).findAll('a')[-1]
            link = nextlink['href']
            count = count + 1
            #print(count)
            #input()
        except:
            break
        
  
        
    return data


def scrape():
    #print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    #print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
