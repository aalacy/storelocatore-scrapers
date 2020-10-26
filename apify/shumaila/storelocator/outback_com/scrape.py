#http://outback.com/
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    chrome_path = 'c:\\Users\\Dell\\local\\chromedriver'
    return webdriver.Chrome('chromedriver', chrome_options=options)
    #return webdriver.Chrome(chrome_path, chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    # Your scraper here
    data = []
    prov = []
    p = 1
    url = 'https://www.outback.com/locations/directory'

    driver1 = get_driver()
    
    driver1.get(url)

    time.sleep(10)
    '''try:
        closeb = driver1.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[1]/div/div/div/div[2]/span')
        closeb.click()
    except:
        time.sleep(20)
        closeb = driver1.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[1]/div/div/div/div[2]/span')
        closeb.click()'''

    province_box = driver1.find_element_by_id("mainContent")
    poption = province_box.find_elements_by_tag_name('option')
    check = 0
    print(len(poption))
    for i in range(1,len(poption)):
        s1 = Select(driver1.find_element_by_id("mainContent"))
        s1.select_by_visible_text(poption[i].text)
        #print(poption[i].text)
        time.sleep(2)
        flag = True
        while flag:
            try:
                maindiv = driver1.find_elements_by_class_name('displayName')
                j=0
                while j < len(maindiv):
                    try:
                        title = maindiv[j].find_element_by_tag_name('a').text
                        link = maindiv[j].find_element_by_tag_name('a').get_attribute('href')
                        link1 = link.replace("https://www.outback.com/locations","https://www.outback.com/partial/location/")
                        #print(link1)
                        page = requests.get(link1)
                        soup = BeautifulSoup(page.text,"html.parser")
                        detail = str(soup.find('jsonpush'))
                        #print(detail)
                        start = detail.find('Address')
                        start = detail.find(':',start)+2
                        end = detail.find('"', start)
                        street = detail[start:end]
                        start = detail.find('id=')
                        if start != -1:
                            start = detail.find('=', start) + 1
                            end = detail.find('"', start)
                            store = detail[start:end]
                        else:
                            store = "<MISSING>"
                        start = detail.find('City')
                        start = detail.find(':', start) + 2
                        end = detail.find('"', start)
                        city = detail[start:end]
                        start = detail.find('"Longitude"')
                        start = detail.find(':', start) + 2
                        end = detail.find('"', start)
                        longt = detail[start:end]
                        start = detail.find('"Latitude"')
                        start = detail.find(':', start) + 2
                        end = detail.find('"', start)
                        lat = detail[start:end]
                        start = detail.find('"Phone"')
                        if start != -1:
                            start = detail.find(':', start) + 2
                            end = detail.find('"', start)
                            phone = detail[start:end]
                        else:
                            phone = "<MISSING>"
                        start = detail.find('"State"')
                        start = detail.find(':', start) + 2
                        end = detail.find('"', start)
                        state = detail[start:end]
                        start = detail.find('"Zip"')
                        start = detail.find(':', start) + 2
                        end = detail.find('"', start)
                        pcode = detail[start:end]

                        hours = soup.find('p',{'ng-html-compile':'CurrentLocation.StoreHoursHtml'}).text
                        hours = hours.lstrip()
                        hours = hours.rstrip()
                        hours = hours.replace("PM","PM ")
                        hours = hours.replace("\n","")
                        if len(hours) < 3:
                            hours = "<MISSING>"
                        #print(hours)
                        data.append([
                            'https://www.outback.com/',
                            link,
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            "US",
                            store,
                            phone,
                            "<MISSING>",
                            lat,
                            longt,
                            hours
                        ])
                        # print(p)
                        #print(p, ",", data[p - 1])
                        p += 1
                        j += 1

                    except:
                        pass
                    flag = False
            except:
                pass


    driver1.quit()
    return data

def scrape():

    data = fetch_data()
    write_output(data)


scrape()
