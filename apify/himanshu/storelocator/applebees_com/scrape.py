import csv
from bs4 import BeautifulSoup
import time
import random
import re
import json
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import TimeoutException
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import platform
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('applebees_com')




show_logs = False

thread_local = threading.local()


def log(*args, **kwargs):
  if (show_logs == True):
    logger.info(" ".join(map(str, args)), **kwargs)
    logger.info("")


def get_time():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)


def firefox(user_agent=None, executable_path=None, headless=True):

    DEFAULT_PROXY_URL = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"

    firefox_options = webdriver.FirefoxOptions()
    seleniumwire_options = {
        'verify_ssl': True,
        'connection_keep_alive': True
    }

    if 'PROXY_PASSWORD' in os.environ:
        log('configuring proxy ...')
        proxy_password = os.environ["PROXY_PASSWORD"]
        url = os.environ["PROXY_URL"] if 'PROXY_URL' in os.environ else DEFAULT_PROXY_URL
        proxy_url = url.format(proxy_password)
        seleniumwire_options = {
            'connection_timeout': None,
            'proxy': {
                'https': proxy_url,
                'http': proxy_url
            }
        }

    if user_agent:
        firefox_options.add_argument('--user-agent=%s' % user_agent)

    if not executable_path:
        executable_path = 'geckodriver'

    if headless:
        firefox_options.add_argument('--headless')

    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-dev-shm-usage')
    firefox_options.add_argument('--window-size=1920,1080')

    capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
    capabilities['locationContextEnabled'] = False

    profile = webdriver.FirefoxProfile()
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.set_preference("dom.webnotifications.enabled", False)
    profile.set_preference("geo.enabled", False)
    profile.set_preference("geo.provider.use_corelocation", False)
    profile.set_preference("geo.prompt.testing", False)
    profile.set_preference("geo.prompt.testing.allow", False)
    profile.update_preferences()

    driver = webdriver.Firefox(desired_capabilities=capabilities, firefox_profile=profile, executable_path=executable_path, firefox_options=firefox_options,
                               seleniumwire_options=seleniumwire_options)

    driver.set_page_load_timeout(20)

    # avoid loading any of these third-party requests ...
    # locally it works rewriting to about:blank, but that resulted in dns errors when run in docker
    driver.rewrite_rules = [
        (r'(https?://)(.*)facebook(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)googleapis(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)contentsquare(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)gstatic(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)twitter(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)pinterest(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)bing(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)google-analytics(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)doubleclick(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)pinimg(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)google(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)adxcel-ec2(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)fontawesome(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)googletagmanager(.*)', r'https://httpbin.org/status/200'),
        (r'(https?://)(.*)myfonts(.*)', r'https://httpbin.org/status/200'),
        # (r'(https?://)(.*)apple(.*)', r'about:blank'), # this one appears to be required for some reason (?)
    ]

    return driver


def create_driver():
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17'
    executable_path = None
    system = platform.system()
    if "linux" in system.lower():
        executable_path = './geckodriver'
    elif "darwin" in system.lower():
        executable_path = './geckodriver-mac'
    else:
        executable_path = 'geckodriver.exe'

    return firefox(executable_path=executable_path, user_agent=user_agent, headless=True)


def get_driver(reset=False, check_proxy_IP=False):
    # give each thread its own driver object.
    # note: when using Apify proxy with seleniumwire, it appears that the IP is automatically rotated between every request.

    if (not hasattr(thread_local, "driver")) or (reset == True):
        log(f'Creating driver for thread {threading.current_thread().ident}')

        if (hasattr(thread_local, "driver")):
            # thread_local.driver.close()
            thread_local.driver.quit()
            del thread_local.driver

        thread_local.driver = create_driver()
        if check_proxy_IP:
            # log the IP address this proxy is using
            # ip = get_ip(thread_local.driver, wait=WebDriverWait(thread_local.driver, 15))
            # log(ip)
            wait = WebDriverWait(thread_local.driver, 15)
            thread_local.driver.get('view-source:https://ipv4.jsonip.com/')
            try:
                pre = wait.until(presence_of_element_located(
                    (By.TAG_NAME, "pre"))).text
                data = json.loads(pre)
                del thread_local.driver.requests
                log(f'Thread {threading.current_thread().ident} IP: {data["ip"]}')
            except TimeoutException as exto:
                log(f'Thread {threading.current_thread().ident} timed out waiting for IP check: {exto}')
            except Exception as ex:
                log(f'Exception on thread {threading.current_thread().ident}: {ex}')

    return thread_local.driver


def quit_driver():
    # optionally, we can call this after each request is finished to ensure a new driver is created for the next request.
    # this slows down the script a lot, but it's the only way I've found to make sure all the drivers on every thread are cleaned up
    #   after the thread pool finishes. probably not an issue in production b/c the docker container is ephemeral.
    if (hasattr(thread_local, "driver")):
        thread_local.driver.quit()
        del thread_local.driver


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


def get_stores(url, reset=False, attempts=1):
    stores = []
    max_attempts = 5
    if attempts > max_attempts:
        log(f'----- max attempts ({max_attempts}) exceeded getting stores from {url}, giving up -----')
        return stores

    driver = get_driver(reset=reset)

    req = None
    try:
        log(f'getting - -> {url} with thread {threading.current_thread().ident} (attempt: {attempts})')
        driver.get(url)

        # Wait for the API request/response to complete
        #   https://pypi.org/project/selenium-wire/#waiting-for-a-request
        req = driver.wait_for_request(
            '/api/sitecore/Locations/LocationSearchAsync', timeout=120)
        if not req.response:
            log(f'no response for {req.path}')
        else:
            log(f'----{url} -- {req.path} -- status {req.response.status_code}')

    except TimeoutException as texc:
        log(f'------- timeout error on thread {threading.current_thread().ident}: {url} ', texc)
        log(f'------- resetting driver on {threading.current_thread().ident} ...')
        time.sleep(2)
        return get_stores(url, reset=True, attempts=attempts+1)
    except Exception as ex:
        log("------- exception getting: ", url, ex)
        time.sleep(2)
        return get_stores(url, reset=True, attempts=attempts+1)

    if not req:
        log('************ no API request found :( **************')
        raise SystemExit

    data = json.loads(req.response.body)

    # clear the captured requests, otherwise they don't get overwritten on the next request (!)
    #   - this was so confusing the first few times b/c the scraper would only find a handful of locations
    del driver.requests

    for location in data['Locations']:

        base_url = "https://www.applebees.com"
        locator_domain = base_url
        location_type = "presidentebarandgrill"

        loc = location["Location"]
        country_code = loc["Country"]
        latitude = loc["Coordinates"]["Latitude"]
        longitude = loc["Coordinates"]["Longitude"]
        page_url = base_url + \
            loc["WebsiteUrl"] if loc["WebsiteUrl"] else '<MISSING>'
        location_name = loc["Name"]
        street_address = loc["Street"]
        city = loc["City"]
        state = loc["State"]
        zipp = loc["Zip"]
        store_number = loc["StoreNumber"]

        phone = location["Contact"]["Phone"]

        days_of_operation = location["HoursOfOperation"]["DaysOfOperation"]
        hours = [
            f'{day["DayofWeek"]}: {day["OpenHours"] or "Closed"}{" - " + day["CloseHours"] if day["OpenHours"] else ""}' for day in days_of_operation]
        hours_of_operation = ", ".join(hours)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        log(store)

        stores.append(store)

    # quit_driver()
    return stores


def get_city_urls(reset=False, attempts=1):
    log('getting city page urls')
    max_attempts = 5
    sitemap_url = "https://www.applebees.com/en/sitemap"
    city_urls = []

    if attempts > max_attempts:
        logger.info(f'Max attempts ({max_attempts}) exceeded getting city urls from {sitemap_url}')
        quit_driver()
        raise SystemExit

    try:
        driver = get_driver(reset=reset)
        driver.get(sitemap_url)
    except Exception as ex:
        log(f'----- exception getting {sitemap_url} : {ex} \n trying again ...')
        return get_city_urls(reset=True, attempts=attempts+1)

    status_code = driver.requests[0].response.status_code if driver.requests[0].response else None
    log('status: ', status_code)
    # logger.info('driver.requests[0] body', driver.requests[0].response.body)
    # logger.info('driver.page_source', driver.page_source)

    if status_code == 403 or 'Access denied' in driver.title:
        logger.info(f'Status code: {status_code}')
        logger.info('Access denied, trying again ... ')
        return get_city_urls(reset=True, attempts=attempts+1)
    else:
        wait = WebDriverWait(driver, 30)
        wait.until(presence_of_element_located(
            (By.CSS_SELECTOR, "div.site-map ul a.nav-link")))
        soup = BeautifulSoup(driver.page_source, "lxml")
        for link in soup.find("div", class_="site-map").find_all("ul")[7:]:
            for a in link.find_all("a", class_="nav-link"):
                a = "https://www.applebees.com"+a["href"]
                city_urls.append(a)

        log(f'found {len(city_urls)} city urls')
        quit_driver()
        return city_urls


def fetch_data():

    city_urls = get_city_urls()

    all_stores = []
    max_worker_threads = 8
    with ThreadPoolExecutor(max_workers=max_worker_threads) as executor:
        futures = [executor.submit(get_stores, url) for url in city_urls]
        for result in as_completed(futures):
            stores_in_city = result.result()
            all_stores.extend(stores_in_city)

    log(f'finished ThreadPoolExecutor with {len(all_stores)} total stores')

    unique_location_urls = []
    for store in all_stores:
        page_url = str(store[-1])
        if page_url not in unique_location_urls:
            unique_location_urls.append(page_url)
            store = [x if x else "<MISSING>" for x in store]
            log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            log("data = " + str(store))
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


log(f'starting script at {get_time()}')
scrape()
log(f'finished script at {get_time()}')
