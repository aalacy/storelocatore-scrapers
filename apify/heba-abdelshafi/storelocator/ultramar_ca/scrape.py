from time import sleep
import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from selenium import webdriver
session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options = options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    p = 0
    url = 'https://www.ultramar.ca/en-on/find-services-stations/'
    print(url)
    driver.get(url)    
    while True:
        try:
            driver.find_element_by_xpath('//a[@class="localization__load-more-link"]').click()
        except:
            break
    divlist = driver.find_element_by_id('store_list')
    divlist = BeautifulSoup(divlist.get_attribute('innerHTML'),'html.parser')
    driver.quit()
    divlist = divlist.findAll('li')
    for div in divlist:
        link = 'https://www.ultramar.ca' +div['data-details_url']
        lat = div['data-lat']
        longt = div['data-lng']
        title = div['data-title']
        store = div['data-id']
        street = div['data-address']
        hourlist = div.find('div',{'class':'localization__right-col-item-third-section-infos'}).findAll('span')
        if len(hourlist) > 0:
            hours = ''
            for hr in hourlist:
                hours = hours + hr.text + ' '
        else:
            hours = div.find('div',{'class':'localization__right-col-item-third-section-infos'}).text
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        city,state = soup.findAll('span',{'class':'station__coordinates-line'})[1].text.split(', ')
        state,pcode = state.lstrip().split(' ',1)
        phone = soup.find('a',{'class':'station__coordinates-line'}).text       
        hours = hours.replace('\n','')
        if pcode.find('N5A 2N') > -1:
            pcode ='N5A 2N1'
        data.append([
                        'https://www.ultramar.ca/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'CA',
                        store,
                        phone,
                        '<MISSING>',
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
