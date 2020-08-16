from bs4 import BeautifulSoup
import csv
import string
import re, time, json
import usaddress
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
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://www.potatocornerusa.com/store-locator'
    p = 0
    r = session.get(url, headers=headers, verify=False)    
    r = r.text.split(':{"pages":')[1].split('],"mainPageId"')[0]
    r = r + ']'
    loclist = json.loads(r)
    titlelist = []
    titlelist.append('none')
    for loc in loclist:
        #print(loc)
        title = loc['title']
        if title.find('Locations') > -1:
            slink = 'https://www.potatocornerusa.com/'+loc['pageUriSEO']
            #print(slink)
            r = session.get(slink, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            linklist = soup.findAll('a',{'class':'ca1link'})
            for link in linklist:               
               
                    
                link = link['href']                    
                #print(link)
                page = session.get(link, headers=headers, verify=False)
                soup1 = BeautifulSoup(page.text,'html.parser')
                title = soup1.find('title').text.split('|')[0]
                if title.find('Coming Soon') == -1 and title not in titlelist:
                    titlelist.append(title)
                    ##print(title)
                    #input()
                    phone = 'N/A'
                    divlist = soup1.findAll('div')
                    for div in divlist:
                        if div.text.find('Address') > -1 and div.text.find('Phone') > -1:
                            dtext = re.sub(cleanr,'',str(div))
                            #print(dtext)
                            address = dtext.split('Address:',1)[1].split('Phone Number')[0]
                            phone = dtext.split('Phone Number:',1)[1].split('#mask')[0]                           
                            
                            break
                    datalink = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=json&SingleLine='+title.replace(' ','%20')+'&outfields=placeName,place_addr,phone,url,location'
                    
                    pagedata = session.get(datalink, headers=headers, verify=False).json()["candidates"][0]
                    coord = pagedata['location']
                    longt = str(coord['x'])
                    lat = str(coord['y'])
                    if phone == 'N/A':
                        phone = '<MISSING>'
                    else:
                        phone = phone.replace("\u200e",'').replace("\xa0",'')
                    pcode = "<MISSING>"
                    
                    try:
                         street,city,state = address.split(', ')
                    except:
                        pass
                    
                    try:
                        state,pcode = state.lstrip().split(' ')
                    except:
                        #input()
                        continue
                                    
                    lat = lat[0:5]
                    longt = longt[0:7]
                    data.append([
                        'https://www.potatocornerusa.com/',
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
                        '<MISSING>'
                    ])
                    print(p,data[p])
                    print(datalink)
                    p += 1
                    #input()
                                
                             
                    
                        
     
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

