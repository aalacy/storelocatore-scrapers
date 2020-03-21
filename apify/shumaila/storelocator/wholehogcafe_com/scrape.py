import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress

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
    url = 'https://www.wholehogcafe.com/locations'
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
   
    mainselect = soup.find('select')
    option_list = mainselect.findAll('option')
    for m in range(1,len(option_list)):
        try:
            if True:#option_list[m]['value'].find('dada') == -1:
                link = 'https://www.wholehogcafe.com/locations/' + option_list[m]['value']
                #print(link)
                driver.get(link)
                time.sleep(2)
                maindiv = driver.find_element_by_xpath('/html/body/app-root/div/div/app-locations/div/div/div')
                div_list = maindiv.find_elements_by_tag_name('div')
                #print(len(div_list))
                for j in range(0,len(div_list)):
                    try:
                        if div_list[j].find_element_by_tag_name('h3'):
                            
                            div = BeautifulSoup(div_list[j].get_attribute('innerHTML'), "html.parser")
                            title = div.find('h3').text
                            hours = ''
                            hourd = div.find('table')
                            hourd = hourd.findAll('tr')
                            for tr in hourd:
                                td = tr.findAll('td')
                                hours = hours +" " + td[0].text + " " + td[1].text 
                            #print(hours)
                            #print(div)
                            maindiv= str(div)
                            div = div.text
                            #div = div.replace(title,'')
                            div = div.lstrip()
                            address = div[0:div.find('Phone')]
                            phone = div[div.find('Phone'):len(div)]
                            phone = phone.replace('Phone:','')
                            phone = phone.lstrip()
                            phone = phone[0:phone.find(' ')]

                            start = maindiv.find('/h3>')
                            start = maindiv.find('>',start)+1
                            end =maindiv.find('<br',start)
                            street = maindiv[start:end]
                            #print(street)

                            start = maindiv.find('br/>',end)
                            start = maindiv.find('>',start)+1
                            end =maindiv.find('<br',start)
                            maindiv = maindiv[start:end]
                            maindiv = maindiv.lstrip()
                            #print(maindiv)
                            city = maindiv[0:maindiv.find(' ')]
                            state = maindiv[maindiv.find(' ')+1:maindiv.find(',')]
                            pcode = maindiv[maindiv.find(',')+1:len(maindiv)]
                            #print(pcode)
                            if len(state) > 2:
                                #print("YES")
                                state = state.lstrip()
                                city = city + ' '+state[0:state.find(' ')]
                                #print(state)
                                state = state[state.find(' ')+1:len(state)]
                                #print(state)
                                if len(state) > 2:
                                    state = state.lstrip()
                                    city = city + ' '+state[0:state.find(' ')]
                                    state = state[state.find(' ')+1:len(state)]
                                    
                            city = city.lstrip()
                            city = city.replace(",",'')
                            street = street.replace(",",'')
                            street = street.lstrip()
                            state = state.lstrip()
                            pcode = pcode.lstrip()
                            if city.find('(') > -1:
                               city = city[city.find(')')+2:len(city)]
                           
                            street = street.replace(city,'')
                            street = street.lstrip()
                            if len(street) < 2:
                                street = "<MISSING>"
                            
                            if len(pcode) < 2:
                                pcode = "<MISSING>"
          
                            if len(phone) < 2:
                                phone =  "<MISSING>"
                            data.append([
                            'https://www.wholehogcafe.com/',
                            link,                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            'US',
                            "<MISSING>",
                            phone,
                            "<MISSING>",
                            "<MISSING>",
                            "<MISSING>",
                            hours
                        ])
                        #print(p,data[p])
                        p += 1
                    except Exception as e:
                        #print(e)
                        pass
            
        except Exception as e:
            print(e)
            pass
       

 
        
        
    driver.quit()   
    return data


def scrape():
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    print(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
#
