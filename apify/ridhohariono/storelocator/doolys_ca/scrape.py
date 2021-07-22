import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import sglog
import time
import re


DOMAIN = "doolys.ca"
BASE_URL = "https://www.doolys.ca"
LOCATION_URL = "https://www.doolys.ca/locations-1"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def addy_ext(addy):
    addy = addy.split(",")
    city = addy[0]
    state_zip = addy[1].strip().split(" ")
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def expand_location(driver):
    driver.find_element_by_class_name("i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c").click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "span.HzV7m-pbTTYe-bN97Pc-ti6hGc-z5C9Gb")
        )
    )
    expand = driver.find_elements_by_css_selector(
        "span.HzV7m-pbTTYe-bN97Pc-ti6hGc-z5C9Gb"
    )
    time.sleep(3)
    for row in expand:
        row.click()
    return True


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field.strip()


def get_latlong(url):
    latlong = re.search(r"(-?[\d]*\.[\d]*)\%2C(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    driver = get_driver(
        "https://www.google.com/maps/d/u/1/embed?mid=10tX5h80FPpTJ2AF85_BZzIl5hbo",
        "i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c",
    )
    expand_location(driver)
    single_store = driver.find_elements_by_class_name("HzV7m-pbTTYe-ibnC6b-V67aGc")
    all_store_data = []
    for row in single_store:
        driver.execute_script("arguments[0].click();", row)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "fO2voc-jRmmHf-MZArnb-Q7Zjwb")
            )
        )
        location_name = row.find_element_by_xpath(
            '//*[@id="featurecardPanel"]/div/div/div[4]/div[1]/div[1]/div[2]'
        ).text.strip()
        info = (
            row.find_element_by_xpath(
                '//*[@id="featurecardPanel"]/div/div/div[4]/div[1]/div[2]/div[2]'
            )
            .text.strip()
            .split("\n")
        )
        address = (
            row.find_element_by_xpath(
                '//*[@id="featurecardPanel"]/div/div/div[4]/div[2]/div[2]'
            )
            .text.strip()
            .split(",")
        )
        street_address = address[0].strip()
        city = address[1].strip()
        state = address[2].split()[0].strip()
        zip_code = " ".join(address[2].split()[1:]).strip()
        phone = info[-1].strip()
        phone = info[0].strip().replace("Tel.: ", "")
        if len(info) < 6:
            hours_of_operation = handle_missing(
                ", ".join(info[4:]).replace("Hours of Operation", "").strip()
            )
        else:
            hours_of_operation = handle_missing(
                ", ".join(info[5:]).replace("Hours of Operation", "").strip()
            )
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude, longitude = get_latlong(driver.current_url)
        country_code = "CA"

        store_data = [
            DOMAIN,
            LOCATION_URL,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        log.info("Append {} => {}".format(location_name, street_address))
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
