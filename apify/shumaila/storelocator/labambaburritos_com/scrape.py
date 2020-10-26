import requests
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
    
    url = 'http://labambaburritos.com/location/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
    titlelist = soup.findAll('span',{'class':'vc_tta-title-text'})
    detaillist = soup.findAll('div',{'class':'sc_icons_item_description'})
   
    coords = soup.findAll('iframe')
    m = 0
    p = 0
    print(len(titlelist))
    for i in range(0,len(titlelist)):
        try:
            title = titlelist[i].text
            #print(title)
            detail = detaillist[m]
            detail = detail.findAll('span')
            street = detail[0].text
            state = detail[1].text
            city,state = state.split(',')
            state = state.lstrip()
            state,pcode = state.split(' ')
            phone = detail[2].text
            hourd = detaillist[m+1]
            hourd = hourd.findAll('span')
            hours = ''
            for hour in hourd:
                hours = hours + hour.text+' '
            
            coord = str(coords[i]['src'])
            start = coord.find('!2d')+3
            end = coord.find('!3d',start)
            longt = coord[start:end]
            start = end + 3
            end = coord.find('!2m',start)
            lat = coord[start:end]
            
            
            hours = hours.replace('am',' am')
            hours = hours.replace('pm',' pm')
            hours = hours.replace('\t',' ')
            try:
                m = m + 2
            except:
                pass
        

            data.append(['http://labambaburritos.com',url,title,street,city,state,pcode,
                     'US','<MISSING>',phone,'<MISSING>',lat,longt,hours])
    
   
            #print(p,data[p])
            p += 1

        except:
            break
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
