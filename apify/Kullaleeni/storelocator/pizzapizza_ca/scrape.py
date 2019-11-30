import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    return webdriver.Chrome('chromedriver', chrome_options=options)
    #return webdriver.Chrome('/Users/Dell/local/chromedriver', chrome_options=options)



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    p = 1

    data = []

    pattern = re.compile(r'\s\s+')
    url = 'https://www5.pizzapizza.ca/restaurant-locator'
    page = requests.get(url)
    driver = get_driver()
    driver.get(url)
    time.sleep(1)
    close = driver.find_element_by_class_name('location-modal-x-col')
    close.click()
    soup = BeautifulSoup(driver.page_source,"html.parser")

    main_list = soup.findAll('li',{'class':'smaller'})
    print(len(main_list))
    for li in main_list:
        citylink = li.find('a')
        citylink = 'https://www5.pizzapizza.ca' + citylink['href']
        print(citylink)
        driver.get(citylink)
        time.sleep(1)
        soup1 = BeautifulSoup(driver.page_source, "html.parser")
        maindiv = soup1.findAll('div',{'class':'store-details'})
        print(len(maindiv))
        for div in maindiv:
            link = div.find('a')
            link = "https://www5.pizzapizza.ca" + link['href']
            driver.get(link)
            time.sleep(1)
            soup2 = BeautifulSoup(driver.page_source, "html.parser")
            detail = soup2.find('div',{'class':'single-store'})
            title = detail.find('h2').text
            street = title
            city,state,pcode = detail.find("p").text.split(",")

            hours= detail.find('div',{'class':'store-hours'}).text
            hours = hours.lstrip()
            hours =hours[hours.find(" ")+1:len(hours)]
            hours = hours.replace("day","day ")
            hours = hours.replace("PM","PM ")
            hours = hours.replace("AM", "AM ")
            hours = hours.replace("  ", " ")
            soup2 = str(soup2)
            start = soup2.find('store_id')
            if start != -1:
                start = soup2.find("=", start)+1
                end = soup2.find("&", start)
                store = soup2[start:end]
            else:
                store = "<MISSING>"
            start = soup2.find('lat&q')
            if start != -1:
                start = soup2.find(":", start)+1
                end = soup2.find(",", start)
                lat= soup2[start:end]
            else:
                lat = "<MISSING>"
            start = soup2.find('lng')
            if start != -1:
                start = soup2.find(":", start) + 1
                end = soup2.find(",", start)
                longt = soup2[start:end]
            else:
                longt = "<MISSING>"
            street= street.lstrip()
            title = title.lstrip()
            city = city.lstrip()
            state = state.lstrip()
            pcode = pcode.lstrip()
            data.append([
                'https://www5.pizzapizza.ca/',
                link,
                title,
                street,
                city,
                state,
                pcode,
                "CA",
                store,
                "<MISSING>",
                "<MISSING>",
                lat,
                longt,
                hours
            ])
            #print(p,",",data[p-1])
            p += 1


    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

    #(data)

scrape()


