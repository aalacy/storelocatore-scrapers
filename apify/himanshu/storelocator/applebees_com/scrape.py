import csv
from bs4 import BeautifulSoup
import time
import re
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import Firefox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import TimeoutException
import os
import platform
system = platform.system()

show_logs = False


def log(*args, **kwargs):
  if (show_logs == True):
    print(" ".join(map(str, args)), **kwargs)
    print("")


def get_driver():

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    # profile = webdriver.FirefoxProfile('C:\\Users\\01\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\3fz3yyhy.default-release')
    profile = webdriver.FirefoxProfile()

    # PROXY_HOST = "127.12.12.123"
    # PROXY_PORT = "1234"

    if 'PROXY_PASSWORD' not in os.environ:
        raise SystemExit(
            "Proxy password required. Please set PROXY_PASSWORD environment variable.")
    else:
        DEFAULT_PROXY_URL = "groups-RESIDENTIAL,country-us:{}@proxy.apify.com"
        PROXY_PORT = "8000"
        proxy_password = os.environ["PROXY_PASSWORD"]
        url = os.environ["PROXY_URL"] if 'PROXY_URL' in os.environ else DEFAULT_PROXY_URL
        proxy_url = url.format(proxy_password)
        # log('proxy_url', proxy_url)

    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", proxy_url)
    profile.set_preference("network.proxy.http_port", int(PROXY_PORT))
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.update_preferences()
    desired = DesiredCapabilities.FIREFOX

    # return Firefox(firefox_profile=profile, desired_capabilities=desired,options=options)

    if "linux" in system.lower():
        return Firefox(executable_path='./geckodriver', firefox_profile=profile, desired_capabilities=desired, options=options)
    elif "darwin" in system.lower():
        return Firefox(executable_path='./geckodriver-mac', firefox_profile=profile, desired_capabilities=desired, options=options)
    else:
        return Firefox(executable_path='geckodriver.exe', firefox_profile=profile, desired_capabilities=desired, options=options)


def write_output(data):
    with open('data.csv', mode='w', newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    base_url = "https://www.applebees.com/"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "presidentebarandgrill"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    driver = get_driver()
    wait = WebDriverWait(driver, 30)

    list_urls = []
    driver.get("https://www.applebees.com/en/sitemap")
    soup = BeautifulSoup(driver.page_source, "lxml")
    for link in soup.find("div", class_="site-map").find_all("ul")[7:]:
        for a in link.find_all("a", class_="nav-link"):
            a = "https://www.applebees.com"+a["href"]
            # log(a)
            list_urls.append(a)
    dict_urls = {i: list_urls[i] for i in range(0, len(list_urls))}
    log(dict_urls)

    index1 = 0
    for q in range(0, len(dict_urls), 5):
        if q == 0:
            index1 = 0
            pass
        else:
            for data1 in range(index1, q):
                if data1 in dict_urls:
                    log("data1 == ", data1, "index1 == ", index1, "q == ", q)
                    try:
                        log('getting --> ', dict_urls[data1])
                        driver.get(dict_urls[data1])
                        wait.until(presence_of_element_located(
                            (By.CSS_SELECTOR, "div#location-cards-wrapper div.owl-item")))
                    except TimeoutException as texc:
                        log('------- timeout error getting: ',
                            dict_urls[data1], texc)
                        log('------- closing driver, getting new one ...')
                        driver.close()
                        time.sleep(2)
                        driver = get_driver()
                        wait = WebDriverWait(driver, 30)
                        driver.get(dict_urls[data1])
                        wait.until(presence_of_element_located(
                            (By.CSS_SELECTOR, "div#location-cards-wrapper div.owl-item")))
                    except Exception as ex:
                        log("------- exception getting: ",
                            dict_urls[data1], ex)
                        continue

                    soup1 = BeautifulSoup(driver.page_source, "lxml")
                    loc_section = soup1.find(
                        "div", {"id": "location-cards-wrapper"})
                    loc_blocks = loc_section.find_all("div", class_="owl-item")
                    log('loc blocks found: ', len(loc_blocks))
                    for loc_block in loc_blocks:
                        country_code = loc_block.find(
                            "input", {"name": "location-country"})["value"]
                        geo_code = loc_block.find(
                            "input", {"name": "location-country"}).nextSibling.nextSibling
                        latitude = geo_code["value"].split(",")[0]
                        longitude = geo_code["value"].split(",")[
                            1].split("?")[0]
                        page_url_anchor_tag = loc_block.find(
                            "div", class_="map-list-item-header").find("a")
                        page_url = "<MISSING>" if page_url_anchor_tag is None else "https://www.applebees.com" + \
                            page_url_anchor_tag["href"]
                        location_name = loc_block.find(
                            "div", class_="map-list-item-header").find("span", class_="location-name").text.strip()
                        address = loc_block.find("div", class_="address").find(
                            "a", {"title": "Get Directions"})
                        address_list = list(address.stripped_strings)
                        street_address = " ".join(address_list[:-1]).strip()
                        city = address_list[-1].split(",")[0].strip()
                        state = address_list[-1].split(
                            ",")[1].split()[0].strip()
                        zipp = address_list[-1].split(
                            ",")[1].split()[-1].strip()
                        phone = loc_block.find(
                            "a", class_="data-ga phone js-phone-mask").text.strip()
                        store_number = "<MISSING>"

                        hours_of_operation = ""
                        if page_url == "<MISSING>" or page_url in addresses:
                            log(f'already have {page_url} ... skipping request')
                        else:
                            try:
                                log('getting --> ', page_url)
                                driver.get(page_url)
                                wait.until(presence_of_element_located(
                                    (By.CSS_SELECTOR, "div.hours")))
                            except TimeoutException as texc:
                                log('------- timeout error getting: ',
                                    page_url, texc)
                                log('------- closing driver, getting new one ...')
                                driver.close()
                                time.sleep(2)
                                driver = get_driver()
                                wait = WebDriverWait(driver, 30)
                                driver.get(page_url)
                                wait.until(presence_of_element_located(
                                    (By.CSS_SELECTOR, "div.hours")))
                            except Exception as ex:
                                log("------- exception getting: ", page_url, ex)
                                hours_of_operation = "<MISSING>"

                            soup2 = BeautifulSoup(driver.page_source, "lxml")
                            try:
                                hours_of_operation = " ".join(
                                    list(soup2.find("div", class_="hours").stripped_strings))
                            except:
                                hours_of_operation = "<MISSING>"

                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                        if str(store[-1]) not in addresses:
                            addresses.append(str(store[-1]))

                            store = [x if x else "<MISSING>" for x in store]

                            log("data = " + str(store))
                            log(
                                '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                            yield store
                        else:
                            log('~~~~~~~~~~~ already have this store')
            index1 += 5
            log('----- closing driver, getting new one -----')
            driver.close()
            driver = get_driver()
            wait = WebDriverWait(driver, 30)

    driver.quit()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
