import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #chrome_path = '/Users/Dell/local/chromedriver'
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://lundsandbyerlys.com/our-stores/locations/'
    driver = get_driver()
    driver.get(url)
    time.sleep(5)
    option = driver.find_element_by_xpath("/html/body/div/div[2]/div/div/article/section/div/div[2]/div[1]/div[1]/ul")
    detail = option.find_elements_by_tag_name('li')

    for n in range(0,len(detail)):
        store = detail[n].get_attribute("data-store-id")

        mtext = str(detail[n].find_element_by_class_name('wpsl-addressLeft').text)
        mtext = mtext.replace("\n", "|")
        print(mtext)
        start = 0
        end = mtext.find("|",start)
        title = mtext[start:end]
        start = end + 1
        end = mtext.find("|", start)
        address = mtext[start:end]
        start = end + 1
        end = mtext.find("|", start)
        address = address + " " +mtext[start:end]
        start = end + 1
        end = mtext.find("|", start)
        phone = mtext[start:len(mtext)]

        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1


        container = driver.find_element_by_class_name("wpsl-hours")
        driver.execute_script("arguments[0].style.display = 'block';", container)
        hourslist = container.find_elements_by_tag_name('p')


        if len(hourslist) == 2:
            hours = hourslist[1].text
        else:
            hours = "<MISSING>"
        print(len(hourslist))
        street = street.lstrip()
        city = city.lstrip()
        state = state.lstrip()
        phone = phone.lstrip()
        pcode = pcode.lstrip()

        
        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            store,
            phone,
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            hours
        ])


    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
