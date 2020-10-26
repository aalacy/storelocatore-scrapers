from bs4 import BeautifulSoup
import csv
import string
import re, time,json

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
    p =0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://www.romeospizza.com/locations/'
    r = session.get(url, headers=headers, verify=False)
    
    soup =BeautifulSoup(r.text, "html.parser")
    linklist = soup.find('div',{'class':'location-list'}).findAll('div',{'class':"col-6"})    
    for link in linklist:
        title = link.find('h4').text
        try:
            link = link.select_one('a:contains("More Info")')['href']            
            r = session.get(link, headers=headers, verify=False)
            loc = r.text.split('<script type="application/ld+json">',1)[1].split('</script>',1)[0]
            loc = json.loads(loc)        
            phone = loc['telephone']
            phone = phone.replace('+1','')
            phone = phone[0:3]+'-'+phone[3:6]+'-'+phone[6:10]
            city = loc['address']['addressLocality']
            #title = city
            street = loc['address']['streetAddress']
            state = loc['address']['addressRegion']
            pcode = loc['address']['postalCode']
            lat = loc['geo']['latitude']
            longt = loc['geo']['longitude']
            hourlist = json.loads(str(loc['openingHoursSpecification']).replace("'",'"'))
            hours =''
            for hr in hourlist:
                end = (int)(hr['closes'].split(':')[0])
                if end > 12:
                    end = end -12
                hours = hours + hr['dayOfWeek'] + ' '+hr['opens'] + ' AM - ' +str(end) +':'+hr['closes'].split(':')[1] +' PM '
                
        
        except:
            try:
                content = link.text
                content = re.sub(pattern,'\n',content).lstrip().splitlines()
                #print(content)
                title = content[0]
                street = content[1]
                city,state = content[2].split(', ',1)
                state, pcode =state.lstrip().split(' ',1)
                phone = content[3]
               
                lat = longt = hours = '<MISSING>'
                link = url
                
            except:
                continue
        
        data.append([
                        'https://romeospizza.com',
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
                
        
        
  
           
        
    return data


def scrape():
    data = fetch_data()
    write_output(data)
   

scrape()
