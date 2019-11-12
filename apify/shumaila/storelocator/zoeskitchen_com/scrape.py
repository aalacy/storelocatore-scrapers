#https://zios.com/locations/?disp=all
# https://zoeskitchen.com/locations/search?location=WI
# https://www.llbean.com/llb/shop/1000001703?nav=gn-hp


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
    return webdriver.Chrome('chromedriver')
    #, chrome_options=options
    #return webdriver.Chrome('/Users/Dell/local/chromedriver')



def fetch_data():
    # Your scraper here

    data = []

    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    pattern = re.compile(r'\s\s+')
    flag = True
    for i in range(0,len(states)):
        url = 'https://zoeskitchen.com/locations/search?location=' + states[i]
        #page = requests.get(url)
        driver = get_driver()
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        maindiv = soup.find('div', {'class':'locations-list'})
        div_list = maindiv.findAll('div',{'class':'col-xs-8 col-sm-8 col-md-7 col-lg-7 info'})
        if len(div_list) > 0:
            for div in div_list:
                #print(div.text)
                title = div.find('h3',{'class': 'clickable'}).text
                tlink = title.replace(' ',"-")
                link = "https://zoeskitchen.com/locations/store/" + states[i].lower() +"/" + tlink.lower()

                driver1 = get_driver()
                driver1.get(link)
                time.sleep(1)
                try:
                    soup1 = BeautifulSoup(driver1.page_source, "html.parser")
                    #print(soup1)
                    title = soup1.find("h3",{'class': 'location-title'}).text
                    address = soup1.find('div',{'class': 'address'}).text
                    hours = soup1.find('table',{'class': 'hours'}).text
                    address = address.replace("\n","|")
                    store = soup1.find('a', {'class': 'btn btn-default order-btn'})
                    store = store['href']
                    start = store.find("=") + 1
                    store = store[start:len(store)]
                    phone = soup1.find('a',{'class':'tel'}).text
                    soup1 = str(soup1)
                    start = soup1.find("var location = ")
                    start = soup1.find("lat",start) + 5
                    end = soup1.find(",",start)
                    lat = soup1[start:end]
                    start = soup1.find("lng", end) + 5
                    end = soup1.find("}", start)
                    longt = soup1[start:end]
                    address = address[1:len(address)-1]
                    start = address.find("|")
                    street = address[0:start]
                    start = start + 1
                    end = address.find(",", start)
                    city = address[start:end]
                    start = end + 2
                    end = address.find(" ", start)
                    state =  address[start:end]
                    start = end + 1
                    end = address.find("|", start)
                    pcode =  address[start:end]
                    hours = re.sub(pattern," ",hours)
                    hours = hours.lstrip()
                    if len(hours) < 3:
                        hours = "<MISSING>"
                    if len(phone) < 3:
                        phone = "<MISSING>"

                    print(link)
                    print(title)
                    print(store)
                    print(address)
                    print(street)
                    print(city)
                    print(state)
                    print(pcode)
                    print(hours)
                    print(phone)
                    print(lat)
                    print(longt)
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
                except:
                    pass
                    driver1.quit()
                    break

                driver1.quit()

        driver.quit()

    return data




def scrape():
    data = fetch_data()
    write_output(data)

scrape()

