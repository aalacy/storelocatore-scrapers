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
    print("states = ",len(link_list))
    p = 0
    for rep in link_list:        
        title = rep.find('h4').text
        det = rep.find('div',{'class':'service-details'}).text.splitlines()
        #print(det)
        try:
            hours = rep.find('p',{'class':'hours-row'}).text.replace('\n',' ')
        except:
            hours = rep.findAll('p')[3].text
            if hours.find('VIEW') > -1:
                hours = rep.findAll('p')[2].text   
        if hours.find("Opening") > -1:
            continue
        street = det[1]
        flag = 0
        try:
            city, state = det[2].split(', ')
            state,pcode = state.lstrip().split(' ')
        except:
            flag = 1
            pass
        phone = det[3]       
            
        link = rep.find('p',{'class':'location-links'})
        link = link.find('a')       
        link = 'https://www.fordsgarageusa.com'+ link['href']
        r = session.get(link, headers=headers, verify=False)
        ccode = 'US'
        
        soup = BeautifulSoup(r.text, "html.parser")
        coord = soup.findAll('iframe')
        coord = str(coord[1]['src'])
        coord = coord.split('!2d',1)[1].split('!2m')[0]
        lat,longt = coord.split('!3d')
        if flag == 1:
            try:
                address = soup.findAll('p',{'class':'hours-row'})[1].text
            except:
                address = soup.findAll('p',{'class':'hours-row'})[0].text
            street,city = address.split('\n',1)
            city,state = city.split(', ')
            state,pcode = state.lstrip().split(' ',1)
            
        phone = phone.replace('Phone:','')
        phone = phone.lstrip()
        hours = hours.replace('\n', ' ')
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
