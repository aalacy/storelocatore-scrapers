
#
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
    #options.add_argument("--start-maximized")
    #return webdriver.Chrome('chromedriver', chrome_options=options)
    return webdriver.Chrome('chromedriver',chrome_options=options)


def fetch_data():
    # Your scraper here

    data = []
    statelinks = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.cubesmart.com/storage-locations/'
    p = 1
    driver = get_driver()
    driver.get(url)
    time.sleep(1)


    #soup = BeautifulSoup(page.text, "html.parser")
    soup = BeautifulSoup(driver.page_source, "html.parser")

    state_list = soup.findAll('div',{'class':'bodySeo'})
    print(len(state_list))
    #driver.quit()
    for li in state_list:
        city = li.find('a')
        link = "https://www.cubesmart.com" + city['href']
        start = link.find("ib.adnx")
        if start != - 1:
            start = link.find("http", start)
            end = len(link)
            link = link[start:end]
            link = link.replace("%2F", "/")
            link = link.replace("%3A", ":")

        #print(link)
        #driver = get_driver()
        driver.get(link)
        #time.sleep(1)

        soup2 = BeautifulSoup(driver.page_source, "html.parser")
        try:
            
            phone = soup2.find('span', {'class': 'tel'}).text
            phone = ""
            title = soup2.find('h1').text
            street = soup2.find('span', {'itemprop': 'streetAddress'}).text
            city = soup2.find('span', {'itemprop': 'addressLocality'}).text
            state = soup2.find('span', {'itemprop': 'addressRegion'}).text
            pcode = soup2.find('span', {'itemprop': 'postalCode'}).text
            lat = soup2.find('meta', {'itemprop': 'latitude'})
            lat = lat['content']
            longt = soup2.find('meta', {'itemprop': 'longitude'})
            longt = longt['content']
           
            hdetail = soup2.findAll('h3', {'class': 'csHoursTitle'})
            htimes = soup2.findAll('p', {'class': 'csHoursList'})
            hours = ""
            for n in range(0, len(htimes)):
                hours = hours + hdetail[n].text + " " + htimes[n].text + " "
            hours = hours.replace("PM"," PM ")
            hours = hours.replace("AM", " AM ")
            hours = hours.replace("-","- ")
            hours = hours.replace("  ", " ")
            #hours = re.sub(pattern," ",hours)
            if len(hours) < 3:
                hours = "<MISSING>"
            if len(phone) <3:
                phonelist = soup2.find('div', {'class': 'csFacilityPhone'})
                phonelist = phonelist.findAll('p')
                phone = phonelist[1].text
                if len(phone) <3:
                    phone = phonelist[0].find('span').text
                    if len(phone) <3:
                        phone = "<MISSING>"


            phone = phone.replace('Current Customers:','')
            phone = phone.replace('New Customers:','')
            phone = phone.lstrip()
            start = link.find("storage") + 4
            start =  link.find("storage", start)
            start =  link.find("/",start) + 1
            end = link.find(".",start)
            store = link[start:end]

            #print(title)
            #print(store)
            #print(street)
            #print(city)
            #print(state)
            #print(pcode)
            #print(phone)
            #print(hours)
            #print(lat)
            #print(longt)
            #print(p)
            flag = True
            # print(len(data))



            if flag:
                data.append([
                    'https://www.cubesmart.com',
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

        except:
            pass

        p += 1


    driver.quit()

    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

