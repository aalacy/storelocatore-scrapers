import csv
import re
from bs4 import BeautifulSoup
from lxml import html
import usaddress
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

                
def fetch_data():
    p = 0
    data = []
    url="https://zinburger.com/locations/"
    r  = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,"html.parser")
    divlist = soup.findAll('div',{'class':'fusion-one-third'})
    #print(len(divlist))
                           
    for div in divlist:
        try:
            check =''
            check = div.find('i',{'class':'fa-fusion-box'}).text
            title = div.find('h4').text.split(' ')[0]
            coord = div.find('h4').find('a')['href']
            det = div.find('div',{'class':'fusion-text'}).text
            if det.find('To Order Food for Delivery') > -1:
                det = det[0:det.find('To Order Food for Delivery')]
            if det.find('To place an order') > -1:
                det = det.split('.',1)[1]
            det = det.lstrip().rstrip().splitlines()
            #print(det)         
            m = 0           
            street = det[m]
            m += 1
            if det[m].find(',') == -1 or det[m].find(',') > -1 and det[m].find('#') > -1:
                street = street + ' ' + det[m]
                m += 1
            
            city, state = det[m].split(', ',1)
            #print(statem)
            state = state.lstrip()
            state,pcode= state.split(' ',1)
            
            m += 1
            phone = det[m]           
            try:
                lat,longt = coord.split('@')[1].split(',',1)
            except:
                r = session.get(coord)
                coord = r.url
                lat,longt = coord.split('@')[1].split(',',1)
                
            longt = longt.split(',',1)[0]
            hourd = div.find('div',{'class':'toggle-content'}).findAll('p')
            hours = ''            
            for hr in hourd:
                if hr.text.find("HAPPY") > -1:
                    break
                hours = hours+ hr.text +' '
            if len(hours) < 3:
                hours = '<MISSING>'
            else:
                hours = hours.replace('\n',' ').replace('HOURS ','').lstrip()
            
            data.append(['https://zinburger.com/','https://zinburger.com/locations/',title,street,city,state,pcode,'US','<MISSING>',phone,'<MISSING>',lat,longt,hours])
            #print(p,data[p])         
            p += 1
            
        except Exception as e:
            #print(e)
            pass
     
    return data
def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
