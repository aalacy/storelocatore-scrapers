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
    url = 'https://www.pastosa.com/Articles.asp?ID=264'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': "col-xs-12 col-sm-4"})
   # print("states = ",len(state_list))
    p = 0
    for div in divlist:
        try:
            link = div.find('a')['href']           
            content = re.sub(pattern,'\n',str(div.text)).lstrip()           
            temp = content.split('\n')[0:2]
            title = temp[0]+' ('+temp[1]+')'
            address = content.split('Address')[1].split('\n',1)[1].split('\nHours')[0]
            address=address.split('\n',1)
            street = address[0]
            city,state =address[1].split(', ')
            state,pcode = state.lstrip().split(' ',1)            
            hours = content.split('Hours',1)[1]
            try:
                hours =hours.split('Hours')[1].split('Phone')[0].replace('\n',' ')
            except:
                hours = hours.split('Phone')[0].replace('\n',' ')             
            phone = content.split('Phone')[1].split('\n',1)[1].replace('\n','')           
            hours = hours.replace('pm','pm ').replace('am',' am ').replace('CLOSED','CLOSED ')
            if link == '#':
                link = '<MISSING>'
                store = '<MISSING>'                
            else:
                'https://www.pastosa.com' + link
                store = link.split('=')[1]
            data.append([
                        'https://www.pastosa.com',
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
                        '<MISSING>',
                        '<MISSING>',
                        hours
                    ])
            #print(p,data[p])
            p += 1
            #input()
            
        except Exception as e:
            #print(e)
            pass
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
