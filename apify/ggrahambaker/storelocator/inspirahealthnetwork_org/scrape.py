import csv
import os
from sgselenium import SgSelenium

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.inspirahealthnetwork.org/' 
    ext = 'locations/?sid=1&searchtypeID=0&latitude=39.4787827&longitude=-75.0377502&searchzip=08360&searchdistance=250#search'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    locs = driver.find_elements_by_css_selector('div.location-card-txt')
    link_list = []
    for loc in locs:
        link_tag = loc.find_element_by_css_selector('a')#.get_attribute('href')
        location_name = link_tag.text
        page_url = link_tag.get_attribute('href')
        
        info_raw = loc.find_element_by_css_selector('p').text.split('\n')
        info = []
        for i in info_raw:
            if 'Suit' in i and ',' not in i:
                continue
            if 'Outpatient' in i:
                continue
            if 'Floor' in i:
                continue
            if '1 East' in i:
                continue
            if 'Building' in i:
                continue
            info.append(i)

        street_address = info[0]
        city, state, zip_code = addy_ext(info[1])
        
        phone_number = loc.find_element_by_css_selector('a.addresslink').text.strip()
        if phone_number == '':
            phone_number = '<MISSING>'

        link_list.append([page_url, phone_number, street_address, city, state, zip_code, location_name])

    all_store_data = []
    for info in link_list:
        driver.get(info[0])
        page_url = info[0]

        google_link = driver.find_element_by_css_selector('a.getdirections').get_attribute('href')
        
        start = google_link.find('/@')
        coords = google_link[start + 2:].split(',')
        lat = coords[0]
        longit = coords[1]
        
        cont = driver.find_element_by_css_selector('div#PageContent').text.split('\n')
        
        hours_arr = []
        switch = False
        for c in cont:
            if 'Hours:' in c:
                switch = True
                continue
                
            if 'Parking:' in c:
                break
        
            if switch:
                hours_arr.append(c)
                
        if len(hours_arr) == 0:
            hours = '<MISSING>'
        else:
            hours = ''
            for h in hours_arr:
                
                hours += h + ' '
                
        hours = hours.split('Schedule')[0].split('Visit')[0].split('The goal')[0].split('REQUEST')[0].split('Whether')[0].split('Inspira Sleep')[0].split('Inspira Medical')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        
        phone_number = info[1]
        street_address = info[2]
        city = info[3]
        state = info[4]
        zip_code = info[5]
        country_code = 'US'
        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        location_name = info[6]
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
