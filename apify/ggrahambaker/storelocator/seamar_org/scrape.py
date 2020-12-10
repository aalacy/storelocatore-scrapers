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
    url = 'https://seamar.org/seamar-clinics.html'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    titlelist = []
    urllist = soup.find('div', {'class': "grid-col grid-col-9"}).findAll('a')
   # print("states = ",len(state_list))
    p = 0
    for nowurl in urllist:
        try:
            if nowurl['href'].find('#') > -1:
                continue
        except:
            continue

        url = 'https://seamar.org/'+nowurl['href']    
        #print(url)
        r = session.get(url, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll('dl')
        
        for div in divlist:
            if div.text.find('Address') == -1:
                continue
            title = div.find('dt').text.strip()
            content = div.find('div',{'class':'details'}).findAll('li')
            try:
                address =  re.sub(cleanr,'\n',str(content[1]))
            except:
                continue
            address = re.sub(pattern,'\n',address).strip().splitlines()
            #print(address)
            street = address[0]
            try:
                city,state = address[1].split(', ',1)
            except:
                continue
            if title in titlelist:
                continue
            titlelist.append(title)
            state,pcode = state.split(' ',1)
            phone = '<MISSING>'
            hours = ''
            try:
                phone = div.text.split('P:',1)[1].split('\n',1)[0]
            except:
                pass
            try:
                hours = div.text.split('Hours:',1)[1].split('More',1)[0]
                hours = hours.replace('\n',' ')
            except:
                pass
            '''phone = re.sub(cleanr,'',str(content[2])).strip()
            try:
                hours = re.sub(cleanr,' ',str(content[5])).strip()
            except:
                hours = '<MISSING>'''
            try:
                link = 'https://seamar.org/' + div.find('a')['href']
            except:
                link = '<MISSING>'

            try:
                hours = hours.split('\n',1)[0]
            except:
                pass
            if len(hours) < 2 or hours.strip().replace('\n','') == 'By appointment only':
                hours = '<MISSING>'
            hours = hours.replace('For Appointments:','').replace('P:','').replace(phone,'').replace('p.m.','p.m. ').replace('Closed',' Closed').replace('  ',' ')
            data.append([
                        'https://seamar.org/',
                        link,                   
                        title,
                        street.replace(',',''),
                        city,
                        state.replace(',',''),
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('P:','').strip(),
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        hours.replace('\n',' ').replace('\t',' ').strip().replace('  ','').replace('â\x80\x93','-')
                    ])
            #print(p,data[p])
            p += 1
                
  
    return data


def scrape():   
    data = fetch_data()
    write_output(data)
 

scrape()
