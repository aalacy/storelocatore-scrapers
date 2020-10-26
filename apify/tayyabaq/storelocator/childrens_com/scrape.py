import csv
import os
import re, time
from bs4 import BeautifulSoup
import json
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
    data=[]
    url = "https://www.childrens.com/wps/FusionServiceCMC/publicsearch/api/apollo/collections/Childrens/query-profiles/ls/select?q=*&start=0&rows=100"
    content = session.get(url, headers=headers, verify=False).json()
    #content = json.load(urllib2.urlopen(url))
    res=content['response']
    docs=res['docs']
    print(len(docs))
    lnk = []
    lnk.append('none')
    p = 0
    for i in range(0,len(docs)):
        loc=docs[i]
        l=str(loc)
        pg=(l.split("\'id\': \'"))[1].split("\'")[0]
        #coord=loc['latlng_p']
        #lat=coord.split(",")[0]
        #longt=coord.split(",")[1]
        link = pg
        
       
        page = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(page.content,"html.parser")
        try:
            loc=soup.find("h1",itemprop='name').text
        except:
            continue
        else:
            loc=loc.replace("\u2120","")
            loc=loc.replace("\n","")
            try:
                hrt=soup.find("span",class_="open-hours")
                hrt=hrt['data-hours']
                det = hrt.split(',')
                #print(det)
                hr = ''
                for dt in det:
                    #print("enter")
                    start,end = dt.lstrip().split(' ',1)[1].split('-')
                    end,tag = end.split(':')
                    #print(start,end)
                    endtime = (int)(end)-12
                    if endtime == 11:
                        hr = hr + dt.lstrip().split(' ',1)[0] +' 24 Hours '
                    else:
                    
                        hr = hr +dt.lstrip().split(' ',1)[0] +' '+ start + ' am - '+str(endtime) + ':'+ tag +' pm '
                
                    
            except:
                try:
                    hr = soup.find('div',{'class':'custom-hours'}).text
                except:
                    hr="<MISSING>"
            else:
                hr=hr.replace(" +","")
            if not hr:
                hr="<MISSING>"
            if hr.find('Appointments') > -1:
                hr ="<MISSING>"
            hr = hr.replace('\n',' ').replace('Su-','Sun - ').replace('Mo-','Mon - ').replace('Th ','Thurs ').replace('Fr ','Fri ').replace('Sa ','Sat ')
            #print(hr)
            street=soup.find("span",itemprop="streetAddress").text
            street=street.replace("\n","")
            for i in range(1,10):
                street=street.replace("  "," ")
            
            street=street.lstrip()
            cty=soup.find("span",itemprop='addressLocality').text
            cty=cty.replace(",","")
            ste=soup.find("span",itemprop='addressRegion').text
            zcode=soup.find("span",itemprop='postalCode').text
            zcode=zcode.strip()
            phone=soup.find("span",itemprop='telephone').text            
            if phone.find("CHILD") > -1:
                phone = '844-424-4537'
            coord = soup.find('a',{'class':'directions-link'})['href'].split('@',1)[1].split('/data')[0]
            lat,longt = coord.split(',',1)
            longt = longt.split(',',1)[0]
            if loc in lnk:
                pass
            
            else:
                lnk.append(loc)
                data.append([
                    'https://www.childrens.com/',
                     link,
                     loc,
                     street,
                     cty,
                     ste,
                     zcode,
                     'US',
                     '<MISSING>',
                     phone,
                     '<MISSING>',
                     lat,
                     longt,
                     hr
                     ])
                #print(p,data[p])
                p += 1
            
    
    print(len(data))
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
