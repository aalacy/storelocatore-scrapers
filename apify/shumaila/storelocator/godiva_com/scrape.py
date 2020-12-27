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
    streetlist = []    
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://stores.godiva.com/us.html'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    checkflag= 0
    statelist = soup.findAll('a', {'class': "c-directory-list-content-item-link"})
   # print("states = ",len(state_list))
    p = 0
    for statelink in statelist:
        statelink = 'https://stores.godiva.com/'+statelink['href']      
        r = session.get(statelink, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        citylist = soup.findAll('a', {'class': "c-directory-list-content-item-link"})
        for citylink in citylist:
            citylink = 'https://stores.godiva.com/'+citylink['href']
            citylink = citylink.replace('../','')            
            r = session.get(citylink, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            linklist = []
            linklist = soup.select('a:contains("View Store Page")')
            flag = 0
            if len(linklist) == 0:
                flag = 1
                linklist.append(citylink)        
            if checkflag == 0:
                checkflag = 1
                linklist.append('https://stores.godiva.com/pr/pr/san-juan/525-f-d--roosevelt.html')
                
            for link in linklist:
                if flag == 0:
                    try:
                        link = 'https://stores.godiva.com/'+link['href']
                        link = link.replace('../','')
                    except:
                        pass
                    r = session.get(link, headers=headers, verify=False)
                    soup =BeautifulSoup(r.text, "html.parser")

                #print(link)  
                soup =BeautifulSoup(r.text, "html.parser")
                try:
                    title = soup.find('div',{'class':'info-subtitle'}).text
                except:
                    title = soup.find('meta',{'property':"og:title"})['content'].split(',',1)[0].split('in ',1)[1]
                street = soup.find('span',{'itemprop':'streetAddress'}).text
                if street in streetlist:
                    continue
                streetlist.append(street)
                city = soup.find('span',{'itemprop':'addressLocality'}).text
                state = soup.find('span',{'itemprop':'addressRegion'}).text
                pcode = soup.find('span',{'itemprop':'postalCode'}).text
                try:
                    phone = soup.find('span',{'itemprop':'telephone'}).text
                except:
                    phone = '<MISSING>'
                hours = soup.find('table',{'class':'c-location-hours-details'}).text.replace('PM','PM ').replace('Closed','Closed ')
                hours = hours.replace('Mon','Mon ').replace('Tue','Tue ').replace('Wed','Wed ').replace('Thu','Thu ').replace('Fri','Fri ').replace('Sat','Sat ').replace('Sun','Sun ')
                store = r.text.split('[{id: ',1)[1].split(',',1)[0]
                lat = r.text.split('latitude:',1)[1].split(',',1)[0]
                longt = r.text.split('longitude:',1)[1].split(',',1)[0]
                data.append([
                            'https://godiva.com/',
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
                    
            
    return data


def scrape():
   
    data = fetch_data()
    write_output(data)


scrape()
