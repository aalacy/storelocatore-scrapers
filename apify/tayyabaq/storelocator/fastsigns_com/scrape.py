import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', options=options)


def fetch_data():
    pages_url = [];
    location_name = [];
    links = [];
    countries = [];
    address_stores = [];
    city = [];
    street_address = [];
    zipcode = [];
    ids = [];
    state = [];
    latitude = [];
    longitude = [];
    hours_of_operation = [];
    phone = []
    # Driver
    driver = get_driver()
    driver.get('https://www.fastsigns.com/worldwide')
    time.sleep(3)
    driver.find_element_by_xpath("//select[@name='DataTables_Table_0_length']/option[5]").click()
    stores = driver.find_elements_by_xpath('//tbody/tr/td/a')
    stores_href = [stores[n].get_attribute('href') for n in range(0, len(stores))]
    stores_text = [stores[n].text for n in range(0, len(stores))]
    country = driver.find_elements_by_xpath('//tbody/tr/td[5]')
    address_type = driver.find_elements_by_xpath('//tbody/tr/td[2]')
    print(address_type)
    for n in range(0, len(stores_href)):
        if (('COMING SOON' not in address_type[n].text) and ('COMING SOON!' not in address_type[n].text)) and (
                ('US' in country[n].text) or ('CA' in country[n].text)):
            links.append(stores_href[n])
            
            # print(location_name)
            
            #print(state)

            #countries.append(country[n].text)
    for n in range(0, len(links)):
        print(links[n])
        driver.get(links[n])
        
        time.sleep(5)
        addr = driver.find_element_by_class_name('address').text.replace(",,",",").split("\n")[0].strip()
        #address=addr.strip().split(",")
        if addr.split(",")[0] !="COMING SOON" and addr.split(",")[0]!= "COMING SOON!":
            z= re.findall(r'[0-9]{5}',addr)
            if z== []:
                z=re.findall(r'[A-Z][0-9][A-Z] [0-9][A-Z][0-9]',addr)
                if z==[]:
                    z=""
                else:
                    z=z[-1]
                    addr=addr.replace(z,"")
            else:
                z=z[-1]
                    addr=addr.replace(z,"")
               
            s= re.findall(r'[A-Z]{2}',addr)
            if s==[]:
                s=""
            else:
                s=s[-1]
                addr=addr.replace(s,"")
            state.append(s)
            print('check',re.findall(r'(.*[a-z0-9])[ ,.]*',addr)[0])
            c=address[-3].strip()
            city.append(c)
            
            zipcode.append(z)
            pages_url.append(links[n])   
            street_address.append(addr.replace(c,"").replace(s,"").replace(z,"").replace(",",""))
            print(address)
            print(city)
            print(street_address)
            print(zipcode)
            if len(z)==5:
                countries.append('US')
            else:
                countries.append('CA')
            ids.append(str(links[n]).split('/')[-1].split('-')[0])
            print(ids)
            if driver.find_element_by_class_name('phone').text != "Coming Soon":
                phone.append(driver.find_element_by_class_name('phone').text)
            else:
                phone.append("<MISSING>")
            hours_of_operation.append(driver.find_element_by_xpath('//div[@class="inner"]/div[3]').text+" "+driver.find_element_by_xpath('//div[@class="inner"]/span[1]').text+" "+driver.find_element_by_xpath('//div[@class="inner"]/span[2]').text)
            lat_lon = b = driver.find_element_by_xpath(
                '//a[contains(@href,"https://www.google.com/maps")]').get_attribute('href')
            try:
                latitude.append(lat_lon.split("n/")[1].split(",")[0])
            except:
                latitude.append('<MISSING>')
            try:
                longitude.append(lat_lon.split("n/")[1].split(",")[1])
            except:
                longitude.append('<MISSING>')
    data = []
    for i in range(0, len(street_address)):
        row = []
        row.append('http://fastsigns.com')
        row.append(location_name[i] if location_name[i] else "<MISSING>")
        row.append(street_address[i] if street_address[i] else "<MISSING>")
        row.append(city[i] if city[i] else "<MISSING>")
        row.append(state[i] if state[i] else "<MISSING>")
        row.append(zipcode[i] if zipcode[i] else "<MISSING>")
        row.append(countries[i] if countries[i] else "<MISSING>")
        row.append(ids[i] if ids[i] else "<MISSING>")
        row.append(phone[i] if phone[i] else "<MISSING>")
        row.append("<MISSING>")
        row.append(latitude[i] if latitude[i] else "<MISSING>")
        row.append(longitude[i] if longitude[i] else "<MISSING>")
        row.append(hours_of_operation[i] if hours_of_operation[i] else "<MISSING>")
        row.append(pages_url[i] if pages_url[i] else "<MISSING>")

        data.append(row)

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
