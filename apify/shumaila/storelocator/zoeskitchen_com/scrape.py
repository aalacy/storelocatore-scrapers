#https://zios.com/locations/?disp=all
# https://zoeskitchen.com/locations/search?location=WI
# https://www.llbean.com/llb/shop/1000001703?nav=gn-hp


import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    #return webdriver.Chrome('chromedriver')
    #, chrome_options=options
    return webdriver.Chrome('C:\\Users\\Dell\\local\\chromedriver.exe')



def fetch_data():
    # Your scraper here

    data = []
    p = 0
   

    pattern = re.compile(r'\s\s+')
    flag = True    
    url = 'https://api.zoeskitchen.com/customer-api/customer-stores/summary-by-state'
    r = session.get(url, headers=headers, verify=False)
  
    soup =str(BeautifulSoup(r.text, "html.parser"))
    #print(soup)
    start = soup.find('{',0)+1
    
    while True:        
        start = soup.find('{',start)+1       
        if start == -1:
            break
        
        end = soup.find('}',start)       
        detail = soup[start:end]        
        mstart = detail.find('storeNumber')
        mstart = detail.find(':',mstart)
        mstart = detail.find('"',mstart) + 1
        mend = detail.find('"',mstart)
        store = detail[mstart:mend]        
        mstart = detail.find('name')
        mstart = detail.find(':',mstart)
        mstart = detail.find('"',mstart) + 1
        mend = detail.find('"',mstart)
        title = detail[mstart:mend]
        mstart = detail.find('address')
        mstart = detail.find(':',mstart)
        mstart = detail.find('"',mstart) + 1
        mend = detail.find('"',mstart)
        street = detail[mstart:mend]
        mstart = detail.find('city')
        mstart = detail.find(':',mstart)
        mstart = detail.find('"',mstart) + 1
        mend = detail.find('"',mstart)
        city = detail[mstart:mend]
        mstart = detail.find('state')
        mstart = detail.find(':',mstart)
        mstart = detail.find('"',mstart) + 1
        mend = detail.find('"',mstart)
        state = detail[mstart:mend]
        mstart = detail.find('zip')
        mstart = detail.find(':',mstart)
        mstart = detail.find('"',mstart) + 1
        mend = detail.find('"',mstart)
        pcode = detail[mstart:mend]
        mstart = detail.find('urlFriendlyName')
        mstart = detail.find(':',mstart)
        mstart = detail.find('"',mstart) + 1
        mend = detail.find('"',mstart)
        link = 'https://zoeskitchen.com/locations/store/'+state.lower()+"/"+detail[mstart:mend]        
        page = session.get(link, headers=headers, verify=False)
        soup1 =BeautifulSoup(page.text, "html.parser")
        try:
            hourlist = soup1.find('table',{'class':'hours'})
            hourlist = soup1.findAll('tr')
            hours = ''
            for hourd in hourlist:
                hour = hourd.text
                hour = hour.replace('\n','')
                hours = hours + hour+' '

            
        except:
            hours = "<MISSING>"
        try:
            phone= soup1.find('a',{'class':'tel'}).text
        except:
            phone = "<MISSING>"
        soup1 = str(soup1)
        mstart = soup1.find('lat:')
        if mstart == -1:
            lat = "<MISSING>"
        else:
            mstart = soup1.find(':',mstart) + 1
            mend = soup1.find(',',mstart)
            lat = soup1[mstart:mend]
        mstart = soup1.find('lng:')
        if mstart == -1:
            longt = "<MISSING>"
        else:
        
            mstart = soup1.find(':',mstart) + 1
            mend = soup1.find('}',mstart)
            longt = soup1[mstart:mend]
        
        start = end
        data.append([
                        'https://zoeskitchen.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        store,
                        phone,
                        "<MISSING>",
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

