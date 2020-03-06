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
    #return webdriver.Chrome(chrome_path,chrome_options=options)

def fetch_data():
    # Your scraper here
    data = []
    url = 'https://petescorp.com/home-page/store-locator/'
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
   
    link_list = soup.findAll('div', {'class': 'results_wrapper'})
    print(len(link_list))

    for repo in link_list:
        #store = repo['id']
        #store = store.replace('slp_results_wrapper_','')
        title = repo.find('span',{'class':'location_name'}).text
        start = title.find('PETES')
        start = title.find(' ',start)+1
        end = title.find(' ',start)
        if end == -1:
            end = len(title)
        store = title[start:end]
        street = repo.find('span',{'class':'slp_result_street'}).text
        detail =  repo.find('span',{'class':'slp_result_citystatezip'}).text
        city = detail[0:detail.find(',')]
        detail = detail[detail.find(',')+1:len(detail)]
        detail = detail.lstrip()
        state = detail[0:detail.find(' ')]
        pcode = detail[detail.find(' ')+1:len(detail)]
        phone = repo.find('span',{'class':'slp_result_phone'}).text
        hours = repo.find('span',{'class':'slp_result_hours'}).text
        hours = hours.replace('am', ' am')
        hours = hours.replace('AM', ' AM')
        hours = hours.replace('PM', ' PM')
        hours = hours.replace('pm', ' pm')
        hours = hours.replace('-', ' - ')
        hours = hours.replace('OPEN ','')
        '''direction = repo.find('span',{'class':'slp_result_directions'}).find('a')
        direction = direction['href']
        #print(direction)
        driver.get(direction)
        time.sleep(3)
        link = driver.current_url
        start = link.find('@')+1
        end = link.find(',',start)
        lat = link[start:end]
        start = end + 1
        end = link.find(',',start)
        longt = link[start:end]'''
        if len(hours) < 3:
            hours = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"
        if len(pcode) < 3:
            pcode = "<MISSING>"
        if len(state) < 2:
            state = "<MISSING>"
        if len(city) < 3:
            city = "<MISSING>"
        if len(street) < 3:
            street = "<MISSING>"
        if len(store) < 1 or len(store)>5:
            store = "<MISSING>"
            
        
        #print(link)
        
        data.append([
                            'https://petescorp.com/',
                            'https://petescorp.com/home-page/store-locator/',                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            'US',
                            store,
                            phone,
                            "<MISSING>",
                            "<MISSING>",
                            "<MISSING>",
                            hours
                        ])
        #print(p,data[p])
        p += 1
        
        
    driver.quit()   
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
