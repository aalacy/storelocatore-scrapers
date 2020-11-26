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
    url = 'https://www.kmart.com/stores.html/'   
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    statelist = soup.select("a[href*=stores]")    
    p = 0
    for statenow in statelist:
        if 'https' in statenow['href']:
            break
        statenow = 'https://www.kmart.com'+statenow['href']             
        r = session.get(statenow, headers=headers, verify=False)
        soup = BeautifulSoup(r.text,'html.parser')
        try:
            linklist = soup.find('div',{'id':'cityList'}).select("a[href*=stores]")
        except:
            continue
        for link in linklist:
            link = 'https://www.kmart.com'+link['href']           
            r = session.get(link, headers=headers, verify=False)
            city = r.text.split('city',1)[1].split('"',1)[1].split('"',1)[0]
            state = r.text.split('state = ',1)[1].split('"',1)[1].split('"',1)[0]
            street = r.text.split('address',1)[1].split('"',1)[1].split('"',1)[0]
            pcode = r.text.split('zip = ',1)[1].split('"',1)[1].split('"',1)[0]
            phone = r.text.split('phone',1)[1].split('"',1)[1].split('"',1)[0]
            lat = r.text.split('lat = ',1)[1].split(',',1)[0]
            longt = r.text.split('lon = ',1)[1].split(',',1)[0]
            store = r.text.split('unitNumber',1)[1].split('= ',1)[1].split(',',1)[0]
            soup = BeautifulSoup(r.text,'html.parser')
            title = soup.find('small',{'itemprop':'name'}).text
            hours = soup.text.split('Hours')[1].split('Holiday',1)[0]
            hours = re.sub(pattern,'',hours).replace('pm','pm ').replace('\n',' ')
            hours = hours.replace('day','day ').replace('  ',' ')
            try:
                hours = hours.split('In-Store',1)[0]
            except:
                pass
            try:
                hours = hours.split('Nearby',1)[0]
            except:
                pass
            title = title.replace('Kmart','Kmart ').replace('#',' # ').replace('  ',' ')
            data.append([
                        'https://www.kmart.com/',
                        link,                   
                        title.replace('\xa0','').replace('\t','').replace('\n',''),
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store.replace('"',''),
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
    data = fetch_data()
    write_output(data)
    

scrape()
