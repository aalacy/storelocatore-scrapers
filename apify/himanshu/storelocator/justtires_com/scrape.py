from bs4 import BeautifulSoup
import csv
import string
import re, time, json

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
    p = 0
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    page = 0
    while True:
        url = 'https://www.justtires.com/en-US/shop/_jcr_content/content/store_results.content?currentPage='+str(page)+'&latitude=32.3182314&longitude=-86.902298'
        r = session.get(url, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        try:
            divlist = soup.find('ul', {'class': "store-results__results"}).findAll('li')        
        except:
            break
        for div in divlist:
            title = div.find('h4').text.replace('\n','')
            link = 'https://www.justtires.com'+div.find('h4').find('a')['href']
            content = div.find('div',{'class':'nav-my-store__information-area'}).find('p')['data-location']
            content = json.loads(content)
            street = content['street']
            city = content['city']
            state = content['state']
            pcode = content['zipCode']
            ccode = content['country']
            lat = content['latitude']
            longt = content['longitude']            
            hours = 'Mon - Sun ' + div.find('p',{'class':"nav-my-store__schedule"}).text
            phone = div.find('p',{'class':'telephone'}).text.replace('\n','')
            store = div.find('input',{'name':'storeId'})['value']
            data.append([
                        'https://www.justtires.com/',
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
         #   input()
           
        page = page + 1
        
    

    return data


def scrape(): 
    data = fetch_data()
    write_output(data)
  
scrape()
