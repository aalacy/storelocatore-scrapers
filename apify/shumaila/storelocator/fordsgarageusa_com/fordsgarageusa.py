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
    p = 0
    
    url = 'https://www.fordsgarageusa.com/locations/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    link_list = soup.findAll('div',{'class':'service-content'})
   # print("states = ",len(state_list))
    p = 0
    for rep in link_list:
        link = rep.find('a')
        title = link.text
        maindiv = rep.findAll('p')
        #print(states.text.strip())
        link = 'https://www.fordsgarageusa.com'+ link['href']
        r = session.get(link, headers=headers, verify=False)
        ccode = 'US'
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        detail = soup.findAll('p',{'class':'hours-row'})
        if len(detail)> 0:
            if len(detail) == 2:
                address = detail[1].find('a').text
                hours = detail[0].text
            elif len(detail) == 1:
                address = detail[0].find('a').text
                hours = "<MISSING>"
            try:
                phone = soup.find('h2',{'class':'dark'})
                phone = phone.find('a')
                phone = phone['href']
                phone = phone.replace('tel:1-','')
            except:
                phone =maindiv[2].text
                
            coord = soup.findAll('iframe')
            coord = str(coord[1]['src'])
            start = coord.find('!2d')+3
            end = coord.find('!3d',start)
            longt = coord[start:end]
            start = end + 3
            end = coord.find('!2m',start)
            if end == -1:
               end = coord.find('!3m',start) 
            lat = coord[start:end]
            print(link)
            street = address[0:address.find('\n')]
            address = address[address.find('\n')+1:len(address)]
            city,state = address.split(', ')
            state = state.lstrip()
            state,pcode = state.split(' ')
           
            hours = hours.replace('\n',' ' )
            
            
        else:
            
            street = maindiv[0].text
            street = street.replace('\n','')
            state = maindiv[1].text
            city,state = address.split(', ')
            state = state.lstrip()
            state,pcode = state.split(' ')
            phone =maindiv[2].text
            hourd  = rep.findAll('p',{'class':'hours-row'})
            hours = ''
            if len(hourd) > 0:
                for det in detail:
                    hours = hours + hourd.text +' '
            else:
                hours = "<MISSING>"
            lat = "<MISSING>"
            longt = "<MISSING>"
            

        if len(hours) < 3:
            hours = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"
        if len(lat) < 3:
            lat = "<MISSING>"
        if len(longt) < 3:
            longt = "<MISSING>"
            
        data.append(['https://www.fordsgarageusa.com/',link,title,street,city,state,pcode,
                     'US','<MISSING>',phone,'<MISSING>',lat,longt,hours])
    
   
        #print(p,data[p])
        p += 1
               
                

                
                
            
        
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
