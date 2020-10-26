import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)
#driver3 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver3 = webdriver.Chrome("chromedriver", options=options)
#driver4 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver4 = webdriver.Chrome("chromedriver", options=options)

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
    count=0
    data=[]
    driver.get("https://www.dollartree.com/locations/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.content_area > table > tbody > tr:nth-child(2) > td > p:nth-child(3) > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    for i in range(0,len(name)):
            driver2.get(name[i])
            page_url = name[i]
            #print(page_url)
            time.sleep(1)
            stores1 = driver2.find_elements_by_css_selector('div.content_area > table > tbody > tr:nth-child(2) > td > p > a')
            name_sub = [stores1[m].get_attribute('href') for m in range(0, len(stores1))]
            for j in range(0,len(name_sub)):
                    driver3.get(name_sub[j])
                    page_url = name_sub[j]
                    #print(page_url)
                    time.sleep(1)
                    store_view_details = driver3.find_elements_by_css_selector('div.storeinfo_div > a')
                    store_view_details_lnks = [store_view_details[n].get_attribute('href') for n in range(0, len(store_view_details))]
                    for k in range(0,len(store_view_details_lnks)):
                        driver4.get(store_view_details_lnks[k])
                        time.sleep(1)
                        page_url = store_view_details_lnks[k]
                        #print(page_url)
                        try:
                            location_name = driver4.find_element_by_css_selector('h1.h1_custom').text
                        except:
                            location_name = '<MISSING>'
                        try:
                            store_id = driver4.find_element_by_css_selector('div.detailsPad > div:nth-child(7) > span:nth-child(1)').text
                            store_id = store_id.split("#")[1]
                        except:
                            store_id = '<MISSING>'
                        try:
                            zipcode = driver4.find_element_by_xpath("//span[contains(@itemprop, 'postalCode')]").text.split("-")[0]
                        except:
                            zipcode = '<MISSING>'
                        try:
                            street_addr = driver4.find_element_by_xpath("//span[contains(@itemprop, 'streetAddress')]").text
                            city = driver4.find_element_by_xpath("//span[contains(@itemprop, 'addressLocality')]").text
                            state = driver4.find_element_by_xpath("//span[contains(@itemprop, 'addressRegion')]").text
                        except:
                            try:
                                street_addr = driver4.find_element_by_xpath("//p[contains(@class, 'dc-al')]").text
                                state_city_zip = driver4.find_element_by_css_selector("#body_wrap_i > div.dc-sc-container > p:nth-child(3)").text
                                state = state_city_zip.split(",")[1].split(" ")[-2]
                                city= state_city_zip.split(",")[0]
                                zipcode = state_city_zip.split(",")[1].split(" ")[-1]
                            except:
                                street_addr = '<MISSING>'
                                city = '<MISSING>'
                                state = '<MISSING>'

                        try:
                            country = driver4.find_element_by_xpath("//span[contains(@itemprop, 'addressCountry')]").text
                        except:
                            country ="US"
                        try:
                            phone = driver4.find_element_by_xpath("//div[contains(@itemprop, 'telephone')]").text
                        except:
                            phone = '<MISSING>'
                        try:
                            hours_of_op = driver4.find_element_by_css_selector('div.hours').text.replace("\n", " ")
                        except:
                            hours_of_op = '<MISSING>'
                        try:
                            latitude = driver4.find_element_by_xpath("//meta[contains(@property, 'place:location:latitude')]").get_attribute('content')
                        except:
                            latitude = '<MISSING>'
                        try:
                            longitude = driver4.find_element_by_xpath("//meta[contains(@property, 'place:location:longitude')]").get_attribute('content')
                        except:
                            longitude = '<MISSING>'
                        data.append([
                            'https://www.dollartree.com/',
                            page_url,
                            location_name,
                            street_addr,
                            city,
                            state,
                            zipcode,
                            country,
                            store_id,
                            phone,
                            '<MISSING>',
                            latitude,
                            longitude,
                            hours_of_op
                        ])
                        count = count + 1
                        print(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    driver3.quit()
    driver4.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
