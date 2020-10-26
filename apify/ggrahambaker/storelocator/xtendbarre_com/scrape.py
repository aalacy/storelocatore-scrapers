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
    url = 'https://www.xtendbarre.com/find-a-studio/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    divlist = soup.find('div',{'id':'c_usa'}).findAll('a')
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:       
        link = 'https://www.xtendbarre.com' + div['href']
        #print(link)
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        title = soup.find('a',{'class':'promotion'}).text
        content = soup.find('div',{'class':'wsc_search_studio_info'}).text.lstrip()
        phone = '('+ content.split('(')[1].split('[')[0]
        try:
            street,city,state = content.replace(phone,'').replace(', United States','').split(', ')
        except:
            street,temp,city,state = content.replace(phone,'').replace(', United States','').split(', ')
            street = street + ' ' + temp
        if city == '':
            city =title
        data.append([
                    'https://www.xtendbarre.com/',
                    link,                   
                    title,
                    street,
                    city,
                    state.split('[')[0],
                    '<MISSING>',
                    'US',
                    '<MISSING>',
                    phone,
                    '<MISSING>',
                    '<MISSING>',
                    '<MISSING>',
                    '<MISSING>'
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
