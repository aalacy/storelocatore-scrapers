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
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://theperfectpita.com/locations/'
    #url = 'https://theperfectpita.com/wp-json/wp/v2/pages/192'
    r = session.get(url, headers=headers, verify=False)
    soup =BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll('div',{'class':'et_pb_text_inner'})
    print(len(divlist))
    for div in divlist:
        if len(div) > 1:
            #print(len(div),div.text)
            
            content = re.sub(cleanr,'\n',str(div))
            content = re.sub(pattern,'\n',content).lstrip().splitlines()
            print(content)
            title =content[0] +' '+ content[1]
            street= content[2]
            city,state = content[3].split(', ',1)
            try:
                state,pcode = state.lstrip().split(' ',1)
            except:
                pcode = '<MISSING>'
            phone= '<MISSING>'
            hours = ''
            for i in range(3,len(content)):
                try:
                    if content[i].find('pm') == -1:
                        if content[i].find('.') > -1:                        
                            phone = content[i]
                    elif content[i].find('direction') > -1:
                        break
                    else:
                        hours = hours +content[i] +' '
                except:
                    pass
                        
                    
            if len(hours) < 2:
                hours = '<MISSING>'
            else:
        
                try:
                    hours = hours.split('Hours',1)[1]
                except:
                    pass
            try:
                coord = div.find('a')['href']
                lat,longt = coord.split('sll=',1)[1].split('&',1)[0].split(',')
            except:
                lat = '<MISSING>'
                longt = '<MISSING>'
            print(hours)
            flag = 0
            try:
                check = div.find('img')['src']
                continue
            except:
                pass
           
            data.append([
                        'https://theperfectpita.com/',
                        'https://theperfectpita.com/locations/',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('.PITA',''),
                        '<MISSING>',
                        lat,
                        longt,
                        hours.lstrip()
                    ])
            #print(p,data[p])
            p += 1
            #input()

  
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
