from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone",
                         "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 0    
    url = 'https://lightbridgeacademy.com/center-locator'
    r = session.get(url, headers=headers, verify=False)
    coords =','+r.text.split('var markers = [')[1].split(';',1)[0].lstrip()    
    coords = coords.lstrip().replace('[','').replace(']','').replace("'",'').replace('\n','').split('\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t')   
    coordlist = []
    for i in range(0,len(coords)):
        if len(coords[i]) > 2:
            temp = coords[i].lstrip().replace('\t\t\t\t\t\t\t\t\t\t\t\t','').split(',')[1:]
            coordlist.append(temp)   
    
    page = 1    
    while True:
        url = 'https://lightbridgeacademy.com/center-locator/?page='+str(page)+'&ajax=1'
        #print(url)
        r = session.get(url, headers=headers, verify=False)
        if r.text.find('No additional results found') > -1:
            break
        else:
            soup = BeautifulSoup(r.text,'html.parser')
            divlist = soup.findAll('div',{'class':'locations'})
            for div in divlist:
                title = div.find('h3').text.lstrip()
                link = 'https://lightbridgeacademy.com'+div.find('a')['href']
                #print(link)                
                det = div.find('div',{'class':'info'}).findAll('div')                
                address = det[0].findAll('span')        
                street = address[0].text.lstrip().replace('\t\t\t\t\t\t\t','')
                city=address[1].text.lstrip().replace(',','').replace('\n','')
                state, pcode = address[2].text.lstrip().split(' ',1)
                try:
                    phone = div.find('div',{'class':'phone'}).text.split('P: ')[1].split('F:')[0].replace('\n','').replace('\t\t\t\t\t\t\t','')
                    hours  = div.find('div',{'class':'hours'}).text.replace('\t','').replace('\n',' ')
                    lat = '<MISSING>'
                    longt = '<MISSING>'
                    for i in range(0,len(coordlist)):                
                        #print(coordlist[i][0])
                        if coordlist[i][0].strip().lower().find(title.lstrip().lower().split(',')[0]) > -1:
                            lat = coordlist[i][2]
                            longt = coordlist[i][3]
                            break
                    if len(hours) < 2:
                        hours = '<MISSING>'
                    data.append(['https://lightbridgeacademy.com/',
                                 link,title,street,city.replace('\t\t\t\t\t\t\t',''),
                                 state.replace('\t\t\t\t\t\t\t',''),pcode.replace('\t\t\t\t\t\t\t',''),
                                 'US','<MISSING>',phone,'<MISSING>',
                                 lat,longt,hours])
                    
                    #print(p,data[p])
                    p += 1
                    #input("NEXT")
                except Exception as e:
                    #print(url)
                    #input(e)
                    pass

            page += 1
            #input("PAGE")
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
