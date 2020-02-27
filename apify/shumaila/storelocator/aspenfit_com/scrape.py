import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    return webdriver.Chrome('chromedriver', chrome_options=options)
    #chrome_path = 'c:\\Users\\Dell\\local\\chromedriver.exe'
    #return webdriver.Chrome(chrome_path)

def fetch_data():
    # Your scraper here
    data = []
    url = 'http://www.aspenfit.com/locations.html'
    driver = get_driver()
    #time.sleep(3)
    driver.set_page_load_timeout(30)
    p = 0
    try:
        driver.get(url)
       
    except:
        pass
    time.sleep(3)
    #driver.back()
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
   
    link_list = soup.findAll('table', {'class': 'wsite-multicol-table'})
    print(len(link_list))
    

    for repo in link_list:
        try:
            cols = repo.findAll('td')
            location = cols[0].findAll('span')
            title = location[0].text
            phone = location[1].text
            street = location[2].text
            city,rest = location[3].text.split(',')
            rest = rest.lstrip()
            state,pcode = rest.split(' ')
            
            
           
            hours = cols[1].text
            
            #print(link)
            coords = str(cols[3].find('iframe')['src'])
            start = coords.find('long')
            start = coords.find('=',start)+1
            end = coords.find('&',start)
            longt = coords[start:end]
            start = coords.find('lat')
            start = coords.find('=',start)+1
            end = coords.find('&',start)
            lat = coords[start:end]
            
            hours = hours.replace('\u200b',' - ')
            hours = hours.replace('pm','pm ')
            hours = hours.replace('day','day ')
            hours = hours.replace('night','night ')
            hours = hours.replace('\n',' ')
            hours = hours.replace('  ',' ')
            start = hours.find('CLUB HOURS')
            start =  hours.find(':')+1
            hours = hours[start:len(hours)]
            data.append([
                        'http://www.aspenfit.com/',
                        'http://www.aspenfit.com/locations.html',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        "<MISSING>",
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])
        
            #print(p,data[p])
            p += 1
            
        except:
            pass

    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
