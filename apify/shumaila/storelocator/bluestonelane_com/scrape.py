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
    url = 'https://bluestonelane.com/cafe-and-coffee-shop-locations/?shop-sort=nearest&view-all=1&lat=33.6592896&lng=73.144729'
    driver = get_driver()
    #time.sleep(3)
    driver.set_page_load_timeout(60)
    p = 0
    try:
        driver.get(url)
       
    except:
        pass
    time.sleep(1)
    #driver.back()
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
   
    link_list = soup.findAll('div', {'class': 'img-wrap'})
    print(len(link_list))
    

    for links in link_list:
        link = links.find('a')
        link = link['href']
        try:
            driver.get(link)
        except:
            pass
        
        time.sleep(5)
        #print(link)
        ccode = 'US'
        soup = BeautifulSoup(driver.page_source, "html.parser")
        title = soup.find('h1').text
        #title = title[0:title.find('-')]
        title.lstrip()
        maindiv = soup.find('aside')
        try:
            street = maindiv.find('span',{'id':'yext-address'})
            try:
                store = street['data-yext-location-id']
            except:
                store = "<MISSING>"
            #print(store)
            try:
                street = street.text
            except:
                street = "<MISSING>"
            try:
                city = maindiv.find('span',{'id':'yext-city'}).text
            except:
                city = "<MISSING>"
            try:
                state = maindiv.find('span',{'id':'yext-state'}).text
               
            except:
                state = "<MISSING>"
            try:
                pcode = maindiv.find('span',{'id':'yext-zip'}).text
                
                try:
                    state1,temp = pcode.split(' ')
                    ccode = "CA"
                except:
                    ccode = 'US'
            except:
                pcode = "<MISSING>"
            try:
                phone = maindiv.find('a',{'data-yext-field':'phone'}).text
            except:
                phone = "<MISSING>"
            try:
                hours = maindiv.find('div',{'class':'yext-hours'}).text
                hours = hours.replace('\n',' ')
                hours = hours.lstrip()
                hourscheck = maindiv.find('span',{'class':'hours'}).text
                if len(hourscheck) < 2:
                    hours = "<MISSING>"
            except:
                hours = "<MISSING>"
            try:
                mapdiv = soup.find('div',{'class':'sidebar-map-embed'})
                coords = mapdiv.find('iframe')
                coords = str(coords['src'])
                #print(coords)
                start = coords.find('!2d')+3
                end = coords.find('!3d',start)
                longt = coords[start:end]
                start = end + 3
                end = coords.find('!',start)
                
                lat = coords[start:end]
                
                
            except:
                lat = "<MISSING>"
                longt = "<MISSING>"

            if len(street) <2:
                street = "<MISSING>"
            if len(city) <2:
                city = "<MISSING>"
            if len(state) <2:
                state = "<MISSING>"
            if len(pcode) <2:
                pcode = "<MISSING>"
            if len(ccode) <2:
                ccode = "<MISSING>"
            if len(phone) <2:
                phone = "<MISSING>"
            if len(store) <1:
                store = "<MISSING>"
            if len(lat) <2:
                lat = "<MISSING>"
            if len(longt) <2:
                longt = "<MISSING>"
            if len(hours) <2:
                hours = "<MISSING>"

            if pcode.find('-') == -1:

                data.append([
                        'https://bluestonelane.com/',
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        store,
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
