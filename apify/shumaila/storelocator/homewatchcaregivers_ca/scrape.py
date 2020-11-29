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
    url = 'https://www.homewatchcaregivers.ca/locations/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll('li',{'class':'location'}) 
    p = 0
    for div in divlist:
        title = div.find('h4').text
        lat = div['data-latitude']
        longt = div['data-longitude']
        link = 'https://www.homewatchcaregivers.ca'+div.select_one('a:contains("Website")')['href']
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        phone = soup.find('span',{'itemprop':'telephone'}).text
        street = soup.find('span',{'itemprop':'streetAddress'}).text.replace('\n',' ').replace('\t',' ').strip()
        city = soup.find('span',{'itemprop':'addressLocality'}).text.replace(',','')
        state = soup.find('span',{'itemprop':'addressRegion'}).text
        pcode = soup.find('span',{'itemprop':'postalCode'}).text        
        data.append([
                        'https://www.homewatchcaregivers.ca/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'CA',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        '24/7'
                    ])
        #print(p,data[p])
        p += 1
                
 
    return data


def scrape():
 
    data = fetch_data()
    write_output(data)


scrape()
