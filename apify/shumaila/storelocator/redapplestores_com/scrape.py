import requests
from bs4 import BeautifulSoup
import csv
import usaddress
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('redapplestores_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    #return webdriver.Chrome('/Users/Dell/local/chromedriver',chrome_options=options)

def fetch_data():
    # Your scraper here
    data = []
    p = 1
    #driver = webdriver.Chrome('/Users/Dell/local/chromedriver')
    #driver = webdriver.Chrome('chromedriver')
    driver = get_driver()
    links = []
    prov = []
    url = "http://www.redapplestores.com/store/52974/"
    driver.get(url)
    time.sleep(4)
    container = driver.find_element_by_class_name("disallow")
    container.click()

    province_box = driver.find_element_by_id("province-selector")
    poption = province_box.find_elements_by_tag_name('option')
    for n in range(1,len(poption)):
        # logger.info(poption[n].get_attribute('value'))
        province = poption[n].get_attribute('value')
        prov.append(province)
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for i in range(0, len(prov)):
        s1 = Select(driver.find_element_by_id("province-selector"))
        s1.select_by_value(prov[i])
        logger.info(prov[i])
        logger.info("checking.....")
        city_box = driver.find_element_by_id("city-selector")
        time.sleep(5)
        coption = city_box.find_elements_by_tag_name('option')
        for j in range(1,len(coption)):
            city = coption[j].get_attribute("value")
            link = "http://www.redapplestores.com" + city
            logger.info(link)
            links.append(link)

    driver.quit()

    p = 1
    logger.info(len(links))
    for n in range(0, len(links)):
        link = links[n]
        logger.info(link)
        driver1 = get_driver()
        driver1.get(link)

        scripts = driver1.page_source
        start = scripts.find("article = {")
        if start != -1:
            end = scripts.find("</script>", start)
            scripts = scripts[start:end]
            start = scripts.find("https://www.google.ca/maps")
            if start != -1:
                start = scripts.find("@", start) + 1
                end = scripts.find(",", start)
                lat = scripts[start:end]
                start = end + 1
                end = scripts.find(",", start)
                longt = scripts[start:end]
            else:
                start = scripts.find('"lat"')
                start = scripts.find(":", start) + 1
                end = scripts.find(",", start)
                lat = scripts[start:end]
                start = start = scripts.find('"lon"')
                start = scripts.find(":", start) + 1
                end = scripts.find(",", start)
                longt = scripts[start:end]

            start = scripts.find('"id":', 0)
            start = scripts.find(":", start) + 1
            end = scripts.find(',', start)
            store = scripts[start:end]

            start = scripts.find("address")
            start = scripts.find(":", start) + 2
            end = scripts.find('"', start)
            street = scripts[start:end]

            start = scripts.find("country")
            start = scripts.find(":", start) + 2
            end = scripts.find('"', start)
            ccode = scripts[start:end]

            start = scripts.find("postalzip")
            start = scripts.find(":", start) + 2
            end = scripts.find('"', start)
            pcode = scripts[start:end]

            start = scripts.find("provstate")
            start = scripts.find(":", start) + 2
            end = scripts.find('"', start)
            state = scripts[start:end]

            start = scripts.find("city")
            start = scripts.find(":", start) + 2
            end = scripts.find('"', start)
            city = scripts[start:end]

            start = scripts.find("phone", 0)
            start = scripts.find(":", start) + 2
            end = scripts.find('"', start)
            phone = scripts[start:end]


            start = scripts.find("google_structured_data")
            end = scripts.find("district")
            hdetail = scripts[start:end]
            i = True
            start = 0
            hours = ""
            while i:
                start = hdetail.find("dayOfWeek", start)
                end = hdetail.find("@type", start)
                if end == -1:
                    end = len(hdetail) - 1
                    i = False

                temp = hdetail[start:end]

                start1 = temp.find(":", 0) + 1
                end1 = temp.find("}", start1)
                temp = temp[start1:end1]
                temp = temp.replace('\\', "")
                temp = temp.replace(']', "")
                temp = temp.replace('[', "")
                temp = temp.replace('"', "")
                temp = temp.replace(',', "-")
                hours = hours + "|" + temp
                start = end

            title = "Red Apple - " + city + "," + state

            hours = hours[1:len(hours)]
            if len(hours) < 3:
                hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"

            pcode = pcode.replace("-"," ")

            logger.info(store)
            logger.info(title)
            logger.info(street)
            logger.info(city)
            logger.info(state)
            logger.info(pcode)
            logger.info(ccode)
            logger.info(phone)
            logger.info(hours)
            logger.info(lat)
            logger.info(longt)
            logger.info(p)
            logger.info("......................................")
            data.append([
                "http://www.redapplestores.com/locations.htm",
                title,
                street,
                city,
                state,
                pcode,
                "CA",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours
            ])
            p += 1


    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
