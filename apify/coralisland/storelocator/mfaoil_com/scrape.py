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
    p = 0
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    for statenow in states:
        #print(statenow)
        gurl = 'https://maps.googleapis.com/maps/api/geocode/json?address='+statenow+'&key=AIzaSyCT4uvUVAv4U6-Lgeg94CIuxUg-iM2aA4s&components=country%3AUS'
        r = session.get(gurl, headers=headers, verify=False).json()
        if r['status'] == 'REQUEST_DENIED':
            pass
        else:
            coord = r['results'][0]["geometry"]['location']
            latnow = coord['lat']
            lngnow = coord['lng']
            url = 'https://www.mfaoil.com/store-locator-data/?brands=mfa-oil&searchfilters=&lat='+str(latnow)+'&lng='+str(lngnow)+'&maxdist=100'
            page = session.get(url, headers=headers, verify=False).json()
            #print(len(page))
            if len(page) == 0:
                pass
            else:
                for loc in page:                  
                    
                    store = loc['id']
                    title = loc['location_name'].replace('<br>',' ')
                    street = loc['address']
                    city= loc['city']
                    state = loc['state']
                    pcode = loc['zipCode']
                    lat = loc['latitude']
                    longt = loc['longitude']
                    phone = loc['phone']
                    link = 'https://www.mfaoil.com' +loc['url'].replace('\\','')
                    hourpage = session.get(link, headers=headers, verify=False)
                    soup = BeautifulSoup(hourpage.text,'html.parser')
                    hours = soup.find('div',{'class':'hours'}).text
                    hours = re.sub(pattern,' ',hours).lstrip().replace('\n',' ')
                    try:
                        hours = hours.split('Location',1)[0]
                    except:
                        pass
                    data.append([
                        'https://www.mfaoil.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        'Store',
                        lat,
                        longt,
                        hours
                    ])
                    print(p,data[p])
                    p += 1
                        
                      
            
            
       
      
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
