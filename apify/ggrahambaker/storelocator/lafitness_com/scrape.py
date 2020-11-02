import csv
import os
from sgselenium import SgSelenium
import json
from selenium.webdriver.support.ui import Select
import time
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lafitness_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://lafitness.com/' 
    ext = 'Pages/findclub.aspx'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    state_select = driver.find_element_by_xpath('//*[@title="Select a State"]')

    states = [x for x in state_select.find_elements_by_tag_name("option")]

    abbrs = []
    for state in states:
        val = state.get_attribute('value')
        if val == '-1':
            continue
        abbrs.append(val)

    link_list = []

    for abbr in abbrs:
        base = 'https://lafitness.com/Pages/findclubresultszip.aspx?state='
        
        driver.get(base + abbr)
        num_result_select = driver.find_element_by_xpath('//*[@title="Page size number"]')
        select = Select(num_result_select)
        select.select_by_value('50')
        driver.implicitly_wait(5)
        time.sleep(1)
        hrefs = driver.find_elements_by_xpath('//a[contains(@href,"clubhome.aspx?clubid=")]')

        while True:
            for h in hrefs:
                link_list.append(h.get_attribute('href'))
        
            if len(hrefs) % 50 == 0:
                next_element = driver.find_elements_by_xpath('//a[contains(text(),"Next")]')
                if len(next_element) == 0:
                    break
                next_element[0].click()
                driver.implicitly_wait(5)
                time.sleep(1)
                hrefs = driver.find_elements_by_xpath('//a[contains(@href,"clubhome.aspx?clubid=")]')

            else:
                break
                
    all_store_data = []
    for link in link_list:
        logger.info(link)
        logger.info()
        logger.info()
        logger.info()
        driver.get(link)
        location_name = driver.find_element_by_css_selector('h1.MainTitle').text
        
        if 'Premier Plus' in location_name:
            location_type = 'Premier Plus'
        elif 'Presale' in location_name:
            continue
        else:
            location_type = '<MISSING>'
        
        driver.find_element_by_id('lnkClubHours').click()
        time.sleep(1)
        driver.implicitly_wait(5)
        
        hoursHTML = driver.find_element_by_css_selector('div#divClubHourPanel').get_attribute('innerHTML')
        soup = BeautifulSoup(hoursHTML, 'html.parser')
        rows = soup.find_all('tr')
        hours = ''
        for row in rows:
            cols = row.find_all('td')
            for col in cols:
                if 'HOURS' in col.text:
                    continue
                else:
                    hours += col.text + ' '

        hours = ' '.join(hours.split())
    
        street_address = driver.find_element_by_id('ctl00_MainContent_lblClubAddress').text
        
        city = driver.find_element_by_id('ctl00_MainContent_lblClubCity').text
        state = driver.find_element_by_id('ctl00_MainContent_lblClubState').text
        zip_code = driver.find_element_by_id('ctl00_MainContent_lblZipCode').text
        if len(zip_code.split(' ')) == 2:
            country_code = 'CA'
        else:
            country_code = 'US'
            
        phone_number = driver.find_element_by_id('ctl00_MainContent_lblClubPhone').text.split('\n')
        
        phone_number = phone_number[0]
        
        bing_map = driver.find_element_by_id('aClubmap').get_attribute('href')
        start = bing_map.find('cp=')
        
        coords = bing_map[start + 3:].split('~')
        lat = coords[0]
        longit = coords[1].split('&')[0]

        page_url = link
        store_number = link[link.find('=') + 1:].split('&')[0]
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
