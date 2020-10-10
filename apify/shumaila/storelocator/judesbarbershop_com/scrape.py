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
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.judesbarbershop.com/location/'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('a', {'class': "elementor-button-link"})
    #print(divlist)
    p = 0
    for div in divlist:
        try:
            div = div['href']
            #print(div)
            if div.find('tel') > -1:
                break
            
            r = session.get(div, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")
            linklist = soup.findAll('h2',{'class':'elementor-heading-title'})
            for link in linklist:
                try:
                    link = link.find('a')['href']
                    print(link)
                    r = session.get(link, headers=headers, verify=False)
                except:
                    link = div
                loc = r.text.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
                #print(":::",loc)
                loc = loc.replace('\n','')
                loc = re.sub(pattern,'',loc)                
                loc = json.loads(loc)                
                street = loc['address']["streetAddress"]
                city = loc['address']["addressLocality"]
                state = loc['address']["addressRegion"]
                pcode = loc['address']["postalCode"]
                ccode = loc['address']["addressCountry"]
                lat = loc['geo']['latitude']
                longt = loc['geo']['longitude']
                phone = loc['telephone']
                title = loc['name']
                hourlist = loc['openingHoursSpecification']
                hours = ''
                for hour in hourlist:
                    start = (int)(hour['opens'].split(':')[0])
                    if start > 12:
                        start = end -12
                    end = (int)(hour['closes'].split(':')[0])
                    if end > 12:
                        end = end -12
                    hours = hours + hour['dayOfWeek'] +' ' + str(start) +":"+hour['opens'].split(':')[1] + ' AM - ' +str(end) +":"+hour['closes'].split(':')[1] + ' PM  '
                    
                
            
                data.append([
                            'https://www.judesbarbershop.com',
                            link,                   
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
                            hours
                        ])
                #print(p,data[p])
                p += 1
                    
            
            
        except Exception as e:            
            pass
        
           
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
