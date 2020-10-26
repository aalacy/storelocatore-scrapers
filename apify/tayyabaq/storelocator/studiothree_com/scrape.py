import csv
import re, time
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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


def parse_geo(url):
    lon = re.findall(r'(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    #Variables
    data=[]
    url = 'https://studiothree.com/location/'
    r = session.get(url, headers=headers, verify=False)
    p = 0
    soup =BeautifulSoup(r.text, "html.parser")
    # Fetch stores
    divlist = soup.findAll('div',{'class':'two-col-f'})
    print((len(divlist)))
    for n in range(0,len(divlist)-2):
        title = divlist[n].find('h6').text
        try:
            street = divlist[n].find('span',{'itemprop':'streetAddress'}).text
        except:
            street = '<MISSING>'
        try:
            city = divlist[n].find('span',{'itemprop':'addressLocality'}).text
        except:
            city = '<MISSING>'
        try:
            state = divlist[n].find('span',{'itemprop':'addressRegion'}).text
        except:
            state = '<MISSING>'
        try:
            pcode = divlist[n].find('span',{'itemprop':'postalCode'}).text
        except:
            pcode = '<MISSING>'
        try:
            phone = divlist[n].find('p',{'itemprop':'telephone'}).text
        except:
            phone = '<MISSING>'
        try:
           
            coord = divlist[n].find('a')['href']
            lat, longt = parse_geo(coord)
        except:
            lat =  '<MISSING>'
            longt =  '<MISSING>'
            
        data.append([
                        'https://studiothree.com/',
                        'https://studiothree.com/location/',                   
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
                        '<MISSING>'
                    ])
        #print(p,data[p])
        #p += 1
        
   
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
    
