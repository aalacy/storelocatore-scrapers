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
    
    streetlist = []
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    for statenow in states:
        #print(statenow)
        page = 0
        gurl = 'https://maps.googleapis.com/maps/api/geocode/json?address='+statenow+'&key=AIzaSyCT4uvUVAv4U6-Lgeg94CIuxUg-iM2aA4s&components=country%3AUS'
        r = session.get(gurl, headers=headers, verify=False).json()
        if r['status'] == 'REQUEST_DENIED':
            pass
        else:
            coord = r['results'][0]["geometry"]['location']
            latnow = coord['lat']
            longnow = coord['lng']
      
        while True:
            url = 'https://www.justtires.com/en-US/shop/_jcr_content/content/store_results.content?currentPage='+str(page)+'&latitude='+str(latnow)+'&longitude='+str(longnow)
            #print(url)
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
                if street in streetlist:
                    continue
                streetlist.append(street)
                city = content['city']
                state = content['state']
                pcode = content['zipCode']
                ccode = content['country']
                lat = content['latitude']
                longt = content['longitude']            
                hours = 'Mon - Sat: ' + div.find('p',{'class':"nav-my-store__schedule"}).text +' Sun: Closed
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
