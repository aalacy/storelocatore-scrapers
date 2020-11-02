import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import time
import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('doolys_ca')



session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    r = session.get("https://www.doolys.ca/locations-1")
    soup = BeautifulSoup(r.text, "lxml")
    iframe_link = soup.find("iframe")["src"]
    r = session.get(iframe_link)
    soup = BeautifulSoup(r.text, "lxml")
    geo_location = {}
    for script in soup.find_all("script"):
        if "_pageData" in script.text:
            location_list = json.loads(script.text.split('var _pageData = "')[1].split('\n";')[0].replace(
                '\\"', '"').replace(r"\n", "")[:-2].replace("\\", " "))[1][6]  # [0][12][0][13][0]
            for state in location_list:
                locations = state[4]
                for location in locations:
                    geo_location[location[5][0][0].replace(
                        " u0027s", "'s").strip().lstrip()] = location[4][0][1]
    driver = SgSelenium().firefox()
    addresses = []
    driver.get(iframe_link)
    time.sleep(3)
    driver.find_element_by_xpath(
        "//div[@class='i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c']").click()
        # for button in
    try:
        for button in driver.find_elements_by_xpath("//div[@class='uVccjd HzV7m-pbTTYe-KoToPc-ornU0b-hFsbo HzV7m-KoToPc-hFsbo-ornU0b']"):
            #logger.info(j.click())

            time.sleep(3)
            button.click()
    except:
        pass
    # fO2voc-jRmmHf-MZArnb-Q7Zjwb
    # fO2voc-jRmmHf-MZArnb-Q7Zjwb
    for button in driver.find_elements_by_xpath("//div[contains(@index, '')]"):
        # logger.info("======================== ",button.get_attribute("index"))
        try:
            try:
                driver.find_element_by_xpath(
                    "//div[@class='U26fgb mUbCce p9Nwte HzV7m-tJHJj-LgbsSe qqvbed-a4fUwd-LgbsSe']").click()
            except:
                pass
            if button.get_attribute("index") == None:
                continue
            time.sleep(3)
            button.click()
            time.sleep(4)
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            name = list(location_soup.find(
                "div", text=re.compile("name")).parent.stripped_strings)[1]
            address = list(location_soup.find("div", text=re.compile(
                "Details from Google Maps")).parent.stripped_strings)[1]
            street_address = address.split(",")[0]
            city = address.split(",")[1]
            store_zip_split = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', address)
            if store_zip_split:
                store_zip = store_zip_split[-1]
            else:
                store_zip = "<MISSING>"
            # logger.info(store_zip)
            state_split = re.findall("([A-Z]{2})", address)
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"
            location_details = list(location_soup.find(
                "div", text=re.compile("description")).parent.stripped_strings)
            for detail in location_details:
                if "Tel" in detail:
                    phone = detail.split("Tel")[1]
            for i in range(len(location_details)):
                if "Hours of Operation" in location_details[i]:
                    hours = " ".join(location_details[i + 1:])
                    break
            store = []
            store.append("https://www.doolys.ca")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone.replace(".:", "").replace(
                "\xa0", "").replace('& Fax: ', "") if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(geo_location[name][0])
            store.append(geo_location[name][1])
            store.append(hours.replace("\xa0", "") if hours else "<MISSING>")
            store.append('https://www.doolys.ca/locations-1')
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
            # logger.info('data == ' + str(store))
            # logger.info('~~~~~~~~~~`````````````')
            yield store
            time.sleep(5)
            driver.find_element_by_xpath(
                "//div[@class='U26fgb mUbCce p9Nwte HzV7m-tJHJj-LgbsSe qqvbed-a4fUwd-LgbsSe']").click()
        except Exception as e:
            # logger.info(",",e)
            time.sleep(3)
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
